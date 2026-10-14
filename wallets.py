"""Server-scoped game currency. No dice calls or Rigger state are involved."""

import json
import re
from .errors import require
from .display import length

MAX_WALLETS = 25
MAX_MONEY = 1_000_000_000_000
PAGE_SIZE = 5
MOD_PERMISSIONS = ('administrator', 'manage_guild', 'manage_messages', 'moderate_members', 'kick_members', 'ban_members')


def moderator(interaction):
    """Use actual server permissions, never a role's name or bot ownership."""
    permissions = getattr(interaction.user, 'guild_permissions', None)
    return bool(interaction.guild_id and permissions is not None
                and any(getattr(permissions, permission, False) for permission in MOD_PERMISSIONS))


def snowflake(value):
    require(type(value) is int and 0 < value < 2**64, 'Use this wallet in its Discord server.')
    return str(value)


def text(value, limit, label):
    require(isinstance(value, str) and not any(ord(char) < 32 for char in value), f'Enter a valid {label}.')
    value = ' '.join(value.split())
    require(1 <= length(value) <= limit, f'{label.capitalize()} must be 1–{limit} characters.')
    return value


def amount(value):
    require(isinstance(value, (str, int)) and not isinstance(value, bool) and len(str(value)) <= 30
            and re.fullmatch(r'\d+', str(value).strip()), 'Enter a positive whole amount, such as 100.')
    value = int(str(value).strip())
    require(1 <= value <= MAX_MONEY, 'Choose an amount from 1 to 1 trillion.')
    return value


class Wallets:
    def __init__(self, store, owner_id):
        self.store, self.owner_id = store, owner_id

    def list(self, guild_id):
        return [dict(row) for row in self.store.db.execute(
            'SELECT id,name,currency FROM currency_wallets_v1 WHERE owner=? AND guild=? ORDER BY id',
            (snowflake(self.owner_id), snowflake(guild_id)))]

    def get(self, guild_id, wallet_id):
        require(type(wallet_id) is int and wallet_id > 0, 'Choose a wallet first.')
        row = self.store.db.execute('SELECT id,name,currency FROM currency_wallets_v1 WHERE id=? AND owner=? AND guild=?',
                                    (wallet_id, snowflake(self.owner_id), snowflake(guild_id))).fetchone()
        require(row is not None, 'That wallet is not available in this server. Press Refresh.')
        return dict(row)

    def snapshot(self, guild_id, wallet_id, player_id, *, page=0, page_size=PAGE_SIZE):
        wallet = self.get(guild_id, wallet_id)
        player = snowflake(player_id)
        require(type(page) is int and page >= 0 and type(page_size) is int and 1 <= page_size <= PAGE_SIZE,
                'Choose a valid history page.')
        # Read balance and history consistently if another bot process writes.
        with self.store.transaction():
            row = self.store.db.execute('SELECT balance FROM currency_balances_v1 WHERE wallet=? AND player=?',
                                       (wallet_id, player)).fetchone()
            count = self.store.db.execute('SELECT count(*) FROM currency_ledger_v1 WHERE wallet=? AND player=?',
                                         (wallet_id, player)).fetchone()[0]
            page = min(page, max(0, (count - 1) // page_size))
            entries = [dict(row) for row in self.store.db.execute(
                'SELECT id,actor,delta,balance_after,reason,created_at FROM currency_ledger_v1 '
                'WHERE wallet=? AND player=? ORDER BY id DESC LIMIT ? OFFSET ?',
                (wallet_id, player, page_size, page * page_size))]
        return {'wallet': wallet, 'balance': row['balance'] if row else 0, 'entries': entries, 'count': count,
                'page': page, 'pages': max(1, (count + page_size - 1) // page_size)}

    def _receipt(self, request_id, signature):
        if request_id is None:
            return None
        request = snowflake(request_id)
        row = self.store.db.execute('SELECT signature,result FROM currency_requests_v1 WHERE owner=? AND request=?',
                                   (str(self.owner_id), request)).fetchone()
        if row is None:
            return None
        require(row['signature'] == signature, 'This request already saved a different change. Open a new form.')
        return json.loads(row['result'])

    def _remember(self, request_id, signature, result):
        if request_id is not None:
            self.store.db.execute('INSERT INTO currency_requests_v1 VALUES (?,?,?,?)',
                                 (str(self.owner_id), snowflake(request_id), signature, json.dumps(result)))

    def save(self, actor_id, guild_id, name, currency='coins', *, wallet_id=None, request_id=None):
        require(actor_id == self.owner_id, 'Only the bot creator can create or name wallets.')
        actor, guild = snowflake(actor_id), snowflake(guild_id)
        name, currency = text(name, 32, 'wallet name'), text(currency, 20, 'currency label')
        signature = json.dumps(['wallet', actor, guild, wallet_id, name, currency])
        with self.store.transaction():
            cached = self._receipt(request_id, signature)
            if cached is not None:
                return {**cached, 'replayed': True}
            if wallet_id is not None:
                self.get(guild_id, wallet_id)
            else:
                require(len(self.list(guild_id)) < MAX_WALLETS, 'This server already has 25 wallets. Edit an existing wallet.')
            duplicate = self.store.db.execute('SELECT id FROM currency_wallets_v1 WHERE owner=? AND guild=? AND name_key=?',
                                             (str(self.owner_id), guild, name.casefold())).fetchone()
            require(duplicate is None or duplicate['id'] == wallet_id, 'A wallet with that name already exists in this server.')
            if wallet_id is None:
                wallet_id = self.store.db.execute(
                    'INSERT INTO currency_wallets_v1(owner,guild,name,name_key,currency) VALUES (?,?,?,?,?)',
                    (str(self.owner_id), guild, name, name.casefold(), currency)).lastrowid
            else:
                self.store.db.execute('UPDATE currency_wallets_v1 SET name=?,name_key=?,currency=? WHERE id=?',
                                      (name, name.casefold(), currency, wallet_id))
            result = {'wallet': self.get(guild_id, wallet_id), 'replayed': False}
            self._remember(request_id, signature, result)
            return result

    def change(self, actor_id, guild_id, wallet_id, player_id, value, reason, *, remove=False,
               is_moderator=False, request_id=None):
        require(is_moderator is True, 'Only server moderators can add or remove money. Bot ownership does not bypass this.')
        actor, guild, player = snowflake(actor_id), snowflake(guild_id), snowflake(player_id)
        require(type(remove) is bool, 'Choose Add money or Remove money.')
        delta = amount(value) * (-1 if remove else 1)
        reason = text(reason, 120, 'reason')
        signature = json.dumps(['money', actor, guild, wallet_id, player, delta, reason])
        with self.store.transaction():
            cached = self._receipt(request_id, signature)
            if cached is not None:
                return {**cached, 'replayed': True}
            wallet = self.get(guild_id, wallet_id)
            row = self.store.db.execute('SELECT balance FROM currency_balances_v1 WHERE wallet=? AND player=?',
                                       (wallet_id, player)).fetchone()
            before = row['balance'] if row else 0
            after = before + delta
            require(after >= 0, f'Not enough money. This balance is {before:,} {wallet["currency"]}.')
            require(after <= MAX_MONEY, 'A balance cannot exceed 1 trillion. Use a smaller amount.')
            self.store.db.execute('INSERT INTO currency_balances_v1 VALUES (?,?,?) '
                                  'ON CONFLICT(wallet,player) DO UPDATE SET balance=excluded.balance',
                                  (wallet_id, player, after))
            entry_id = self.store.db.execute('INSERT INTO currency_ledger_v1(wallet,player,actor,delta,balance_after,reason) '
                                            'VALUES (?,?,?,?,?,?)', (wallet_id, player, actor, delta, after, reason)).lastrowid
            result = {'wallet': wallet, 'player': player, 'delta': delta, 'balance': after, 'entry_id': entry_id, 'replayed': False}
            self._remember(request_id, signature, result)
            return result
