"""Private, interactive wallet cards with live moderator checks on every edit."""

import logging
import secrets
import discord
from .display import safe, length
from .errors import RollError
from .wallets import moderator, PAGE_SIZE

log = logging.getLogger(__name__)
NO_MENTIONS = discord.AllowedMentions.none()
TEAL = 0x2DD4BF


async def reply(interaction, content):
    if interaction.response.is_done():
        await interaction.followup.send(content, ephemeral=True, allowed_mentions=NO_MENTIONS)
    else:
        await interaction.response.send_message(content, ephemeral=True, allowed_mentions=NO_MENTIONS)


def shown(value, budget=120):
    result = safe(' '.join(str(value).split()))
    while length(result) > budget:
        result = result[:-1]
    return result.rstrip('\\') or 'Player'


class WalletChoice(discord.ui.Select):
    def __init__(self, panel, wallets):
        self.panel = panel
        options = [discord.SelectOption(label=wallet['name'], value=str(wallet['id']),
                   description=f"Currency: {wallet['currency']}", emoji='🪙', default=wallet['id'] == panel.wallet_id)
                   for wallet in wallets]
        super().__init__(custom_id=panel.key('wallet'), placeholder='Choose a wallet in this server',
                         options=options or [discord.SelectOption(label='No wallets yet', value='none')],
                         disabled=not wallets, row=0)

    async def callback(self, interaction):
        if not await self.panel.authorize(interaction):
            return
        await interaction.response.defer()
        try:
            value = self.values[0]
            if not value.isdecimal() or len(value) > 19:
                raise RollError('Choose a wallet from this server.')
            wallet = self.panel.bot.wallets.get(self.panel.guild_id, int(value))
            self.panel.wallet_id, self.panel.history_page = wallet['id'], 0
            self.panel.note = 'Choose a wallet to track this campaign’s currency.'
            await self.panel.update(interaction)
        except RollError as exc:
            await reply(interaction, '⚠️ ' + safe(exc))


class PlayerChoice(discord.ui.UserSelect):
    def __init__(self, panel):
        self.panel = panel
        super().__init__(custom_id=panel.key('player'), placeholder='Moderator: choose a player', row=1,
                         default_values=[discord.SelectDefaultValue(id=panel.player.id, type=discord.SelectDefaultValueType.user)])

    async def callback(self, interaction):
        if not await self.panel.authorize(interaction, action='mod'):
            return
        await interaction.response.defer()
        try:
            self.panel.player = await self.panel.member(interaction, self.values[0].id)
            self.panel.history_page = 0
            self.panel.note = 'Player selected. Add or remove money with a reason.'
            await self.panel.update(interaction)
        except RollError as exc:
            await reply(interaction, '⚠️ ' + safe(exc))


class WalletInput(discord.ui.Modal):
    def __init__(self, panel, kind):
        self.panel, self.kind = panel, kind
        self.wallet_id, self.player_id = panel.wallet_id, panel.player.id
        editing = kind == 'edit'
        config = kind in ('new', 'edit')
        super().__init__(title={'new': 'Create a wallet', 'edit': 'Edit wallet',
                               'add': 'Add money', 'remove': 'Remove money'}[kind], timeout=180)
        if config:
            wallet = panel.bot.wallets.get(panel.guild_id, self.wallet_id) if editing else None
            self.first = discord.ui.TextInput(default=wallet['name'] if wallet else None,
                                              placeholder='Avatar campaign, UA, savings…', min_length=1, max_length=32)
            self.second = discord.ui.TextInput(default=wallet['currency'] if wallet else 'coins',
                                               placeholder='coins, credits, gold…', min_length=1, max_length=20)
            labels = ('Wallet name', 'Currency label')
        else:
            self.first = discord.ui.TextInput(placeholder='Positive whole number, such as 100', min_length=1, max_length=20)
            self.second = discord.ui.TextInput(placeholder='Quest reward, shop purchase, correction…', min_length=1, max_length=120)
            wallet = panel.bot.wallets.get(panel.guild_id, self.wallet_id)
            labels = (f"Amount · {wallet['currency']}", 'Reason (saved in the history)')
        for label, field in zip(labels, (self.first, self.second)):
            self.add_item(discord.ui.Label(text=label, component=field))

    async def interaction_check(self, interaction):
        return await self.panel.authorize(interaction, action='creator' if self.kind in ('new', 'edit') else 'mod')

    async def on_submit(self, interaction):
        if not await self.interaction_check(interaction):
            return
        try:
            if self.kind != 'new' and self.wallet_id != self.panel.wallet_id:
                raise RollError('The selected wallet changed. Open a new form.')
            if self.kind in ('add', 'remove') and self.player_id != self.panel.player.id:
                raise RollError('The selected player changed. Open a new form.')
            await interaction.response.defer()
            if self.kind in ('new', 'edit'):
                result = self.panel.bot.wallets.save(interaction.user.id, self.panel.guild_id, self.first.value,
                    self.second.value, wallet_id=self.wallet_id if self.kind == 'edit' else None, request_id=interaction.id)
                self.panel.wallet_id = result['wallet']['id']
                self.panel.note = '✅ Wallet saved. Renaming keeps all balances and history.'
            else:
                await self.panel.member(interaction, self.player_id)
                if self.panel.is_finished():
                    raise RollError('This panel has closed. Use /wallet again.')
                result = self.panel.bot.wallets.change(interaction.user.id, self.panel.guild_id, self.wallet_id,
                    self.player_id, self.first.value, self.second.value, remove=self.kind == 'remove',
                    is_moderator=moderator(interaction), request_id=interaction.id)
                self.panel.note = f"✅ {'Already saved' if result['replayed'] else 'Saved'} · {result['delta']:+,} " + shown(result['wallet']['currency'])
            self.panel.history_page = 0
            await self.panel.update(interaction)
        except RollError as exc:
            await reply(interaction, '⚠️ ' + safe(exc))

    async def on_error(self, interaction, error):
        log.warning('Wallet form failed: %s.', type(error).__name__)
        await reply(interaction, 'Could not finish this action. Open /wallet to check the balance before trying again.')


class WalletPanel(discord.ui.View):
    def __init__(self, bot, interaction):
        super().__init__(timeout=600)
        self.bot, self.message = bot, None
        self.author_id, self.guild_id = interaction.user.id, interaction.guild_id
        self.guild_name = getattr(interaction.guild, 'name', 'This server')
        self.player = interaction.user
        self.can_manage = moderator(interaction)
        self.creator = self.author_id == bot.engine.owner_id
        self.nonce = secrets.token_hex(6)
        wallets = bot.wallets.list(self.guild_id)
        self.wallet_id = wallets[0]['id'] if wallets else None
        self.history, self.history_page = False, 0
        self.note = 'Your balances, organised by campaign. Choose a wallet below.'
        self.build_items()

    def key(self, kind):
        return f'wallet:{self.nonce}:{kind}'

    async def authorize(self, interaction, action=None):
        if interaction.user.id != self.author_id or interaction.guild_id != self.guild_id:
            await reply(interaction, 'This is someone else’s wallet panel. Use /wallet in your server.')
            return False
        if self.is_finished():
            await reply(interaction, 'This panel has closed. Use /wallet again; your balances are saved.')
            return False
        self.can_manage = moderator(interaction)
        if not self.can_manage and self.player.id != self.author_id:
            self.player, self.history_page = interaction.user, 0
        if action == 'mod' and not self.can_manage:
            await reply(interaction, 'Only server moderators can add or remove money.')
            return False
        if action == 'creator' and interaction.user.id != self.bot.engine.owner_id:
            await reply(interaction, 'Only the bot creator can create or name wallets.')
            return False
        return True

    async def interaction_check(self, interaction):
        return await self.authorize(interaction)

    async def member(self, interaction, player_id):
        guild = interaction.guild
        if guild is None or guild.id != self.guild_id:
            raise RollError('Use /wallet in its server.')
        try:
            member = await guild.fetch_member(player_id)
        except discord.NotFound:
            raise RollError('That player is no longer in this server. Choose a current member.')
        except discord.HTTPException:
            raise RollError('Could not check that player. Try again in a moment.')
        if member.bot:
            raise RollError('Choose a player account, not a bot.')
        return member

    def snapshot(self):
        if self.wallet_id is None:
            return None
        data = self.bot.wallets.snapshot(self.guild_id, self.wallet_id, self.player.id,
                                       page=self.history_page if self.history else 0, page_size=PAGE_SIZE if self.history else 3)
        self.history_page = data['page']
        return data

    def add_button(self, label, kind, handler, *, row=2, emoji=None, style=discord.ButtonStyle.secondary, disabled=False, action=None):
        button = discord.ui.Button(label=label, custom_id=self.key(kind), row=row, emoji=emoji, style=style, disabled=disabled)
        async def callback(interaction):
            if await self.authorize(interaction, action=action):
                await handler(interaction)
        button.callback = callback
        self.add_item(button)

    def build_items(self):
        self.clear_items()
        wallets = self.bot.wallets.list(self.guild_id)
        if self.wallet_id is None and wallets:
            self.wallet_id = wallets[0]['id']
        self.add_item(WalletChoice(self, wallets))
        if self.can_manage:
            self.add_item(PlayerChoice(self))
            self.add_button('Add money', 'add', self.add_money, emoji='➕', style=discord.ButtonStyle.success,
                            disabled=self.wallet_id is None, action='mod')
            self.add_button('Remove money', 'remove', self.remove_money, emoji='➖', style=discord.ButtonStyle.danger,
                            disabled=self.wallet_id is None, action='mod')
            self.add_button('My balance', 'me', self.my_balance)
        self.add_button('Balance' if self.history else 'History', 'history', self.toggle_history, emoji='📒', disabled=self.wallet_id is None)
        self.add_button('Refresh', 'refresh', self.refresh, emoji='🔄')
        if self.creator:
            self.add_button('New wallet', 'new', self.new_wallet, row=3, emoji='🪙', style=discord.ButtonStyle.primary,
                            disabled=len(wallets) >= 25, action='creator')
            self.add_button('Edit wallet', 'edit', self.edit_wallet, row=3, disabled=self.wallet_id is None, action='creator')
        data = self.snapshot()
        if self.history and data:
            self.add_button('Previous', 'prev', self.previous, row=4, disabled=data['page'] == 0)
            self.add_button('Next', 'next', self.next, row=4, disabled=data['page'] + 1 >= data['pages'])

    def embed(self):
        data = self.snapshot()
        embed = discord.Embed(colour=TEAL)
        embed.set_author(name='Wallets · in-game currency')
        if data is None:
            embed.title = '🪙 Your wallet starts here'
            embed.description = ('Create the first wallet for **' + shown(self.guild_name) + '**.\n'
                                 'Choose a name and currency label; every player starts at zero.' if self.creator else
                                 'No wallets have been created for **' + shown(self.guild_name) + '** yet.\n'
                                 'Ask the bot creator to open /wallet here and choose **New wallet**.')
        else:
            wallet = data['wallet']
            embed.title = '🪙 ' + safe(wallet['name'])
            embed.description = f"**{data['balance']:,} {safe(wallet['currency'])}**\n{self.note}"
            embed.add_field(name='Player', value=shown(self.player.display_name) + f'\n`{self.player.id}`', inline=True)
            embed.add_field(name='Server', value=shown(self.guild_name), inline=True)
            avatar = getattr(getattr(self.player, 'display_avatar', None), 'url', None)
            if avatar:
                embed.set_thumbnail(url=str(avatar))
            entries = []
            for item in data['entries']:
                symbol = '🟢' if item['delta'] > 0 else '🔴'
                entries.append(f"{symbol} **{item['delta']:+,}** · {safe(item['reason'])}\n"
                               f"Balance {item['balance_after']:,} · <t:{item['created_at']}:f> · Mod `{item['actor']}`")
            if entries:
                embed.add_field(name=f"{'History' if self.history else 'Recent activity'} · {data['count']} changes",
                                value=entries[0], inline=False)
                for entry in entries[1:]:
                    embed.add_field(name='Activity', value=entry, inline=False)
            else:
                embed.add_field(name='Recent activity', value='No changes yet. Rewards and spending will appear here.', inline=False)
        mode = 'Moderator' if self.can_manage else 'Your balance'
        page = f" • Page {data['page'] + 1}/{data['pages']}" if data and self.history else ''
        embed.set_footer(text=f'{mode} • Only you see this panel{page} • /wallet to reopen')
        return embed

    async def update(self, interaction):
        # Acknowledge before SQLite's possible lock wait or a history read.
        if not interaction.response.is_done():
            await interaction.response.defer()
        self.build_items()
        if interaction.response.is_done():
            await self.message.edit(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)
        else:
            await interaction.response.edit_message(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)

    async def add_money(self, interaction):
        if self.wallet_id is None:
            await reply(interaction, 'Choose a wallet first.')
            return
        await interaction.response.send_modal(WalletInput(self, 'add'))

    async def remove_money(self, interaction):
        if self.wallet_id is None:
            await reply(interaction, 'Choose a wallet first.')
            return
        await interaction.response.send_modal(WalletInput(self, 'remove'))

    async def new_wallet(self, interaction):
        await interaction.response.send_modal(WalletInput(self, 'new'))

    async def edit_wallet(self, interaction):
        if self.wallet_id is None:
            await reply(interaction, 'Choose a wallet first.')
            return
        await interaction.response.send_modal(WalletInput(self, 'edit'))

    async def refresh(self, interaction):
        self.note = 'Balances refreshed. Every saved change has a reason and moderator ID.'
        await self.update(interaction)

    async def my_balance(self, interaction):
        self.player, self.history_page = interaction.user, 0
        self.note = 'Viewing your own balance.'
        await self.update(interaction)

    async def toggle_history(self, interaction):
        self.history, self.history_page = not self.history, 0
        await self.update(interaction)

    async def previous(self, interaction):
        self.history_page = max(0, self.history_page - 1)
        await self.update(interaction)

    async def next(self, interaction):
        self.history_page += 1
        await self.update(interaction)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message is not None:
            try:
                embed = self.embed()
                embed.set_footer(text='Panel closed • Your balances are saved • /wallet to reopen')
                await self.message.edit(embed=embed, view=self, allowed_mentions=NO_MENTIONS)
            except discord.HTTPException:
                pass

    async def on_error(self, interaction, error, item):
        log.warning('Wallet panel failed: %s.', type(error).__name__)
        await reply(interaction, 'Could not update this panel. Open /wallet to check the current balance.')
