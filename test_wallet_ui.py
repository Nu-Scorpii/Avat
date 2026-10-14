import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import discord
import pytest
from ua_bot.client import DiceBot
from ua_bot.wallet_ui import WalletPanel, WalletInput, PlayerChoice, WalletChoice
from ua_bot.wallets import MOD_PERMISSIONS, moderator
from test_rigger_panel import button, owner_event


def event(request=1000, user=42, guild=100, permissions=()):
    value = owner_event(request, owner=user, guild=guild)
    value.user.display_name = f'Player {user}'
    value.user.guild_permissions = discord.Permissions(**{name: True for name in permissions})
    value.user.bot = False
    value.guild = SimpleNamespace(id=guild, name='Avatar guild', fetch_member=AsyncMock()) if guild else None
    value.edit_original_response.return_value = SimpleNamespace(edit=AsyncMock())
    async def defer(**kwargs):
        value.response.is_done.return_value = True
    value.response.defer.side_effect = defer
    return value


def panel_for(bot, value):
    panel = WalletPanel(bot, value)
    panel.message = SimpleNamespace(edit=AsyncMock())
    return panel


@pytest.mark.parametrize('permission', MOD_PERMISSIONS)
def test_real_moderator_permissions_unlock_currency_controls(permission):
    assert moderator(event(permissions=(permission,)))
    assert not moderator(event(permissions=('manage_roles',)))
    assert not moderator(event(guild=None, permissions=(permission,)))


def test_wallet_slash_opens_a_private_balance_card_and_preserves_roll_controls(make_engine):
    async def check():
        engine = make_engine()
        engine.configure(1, is_dm=True, mode='force', value=20, target=42, scope='avatar', part='iq', uses=3)
        before = engine.control_status(1, is_dm=True)
        bot = DiceBot(engine)
        bot.wallets.save(1, 100, 'Avatar', 'coins')
        current = event()
        await bot.run_wallet(current)
        current.response.defer.assert_awaited_once_with(thinking=True, ephemeral=True)
        payload = current.edit_original_response.await_args.kwargs
        assert payload['embed'].title == '🪙 Avatar' and '**0 coins**' in payload['embed'].description
        assert payload['allowed_mentions'].everyone is False
        panel = payload['view']
        assert not any(isinstance(item, PlayerChoice) for item in panel.children)
        assert not any(getattr(item, 'label', None) in ('Add money', 'Remove money', 'New wallet') for item in panel.children)
        assert engine.control_status(1, is_dm=True) == before and engine.rng.calls == 0
        command = bot.tree.get_command('wallet').to_dict(bot.tree)
        assert command.get('options', []) == [] and command['contexts'] == [0]
        panel.stop()
        await bot.close()
    asyncio.run(check())


def test_wallet_slash_in_dm_replies_privately_without_opening_a_panel(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        current = event(guild=None)
        await bot.run_wallet(current)
        current.response.defer.assert_not_awaited()
        assert current.response.send_message.await_args.kwargs['ephemeral']
        current.edit_original_response.assert_not_awaited()
        await bot.close()
    asyncio.run(check())


def test_creator_can_create_and_name_several_wallets_but_cannot_add_money_without_mod_permissions(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        panel = panel_for(bot, event(user=1))
        assert 'starts here' in panel.embed().title
        for index, name in enumerate(('Avatar campaign', 'UA campaign')):
            modal = WalletInput(panel, 'new')
            modal.first._value, modal.second._value = name, 'coins' if index == 0 else 'credits'
            await modal.on_submit(event(1000 + index, user=1))
            modal.stop()
        assert len(bot.wallets.list(100)) == 2 and bot.wallets.list(200) == []
        selection = next(item for item in panel.children if isinstance(item, WalletChoice))
        selection._values = [str(bot.wallets.list(100)[0]['id'])]
        await selection.callback(event(1002, user=1))
        assert panel.embed().title == '🪙 Avatar campaign'
        forged = WalletInput(panel, 'add')
        forged.first._value, forged.second._value = '100', 'Test'
        await forged.on_submit(event(1003, user=1))
        assert bot.wallets.snapshot(100, panel.wallet_id, 1)['balance'] == 0
        forged.stop()
        panel.stop()
        await bot.close()
    asyncio.run(check())


def test_moderator_can_select_a_player_add_remove_and_browse_history(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        wallet = bot.wallets.save(1, 100, 'Avatar', 'coins')['wallet']['id']
        panel = panel_for(bot, event(user=9, permissions=('manage_messages',)))
        selection = next(item for item in panel.children if isinstance(item, PlayerChoice))
        selected = SimpleNamespace(id=42, display_name='Hero', bot=False)
        selection._values = [selected]
        current = event(1000, user=9, permissions=('manage_messages',))
        current.guild.fetch_member.return_value = selected
        await selection.callback(current)
        assert panel.player.id == 42
        for index in range(7):
            modal = WalletInput(panel, 'add' if index < 6 else 'remove')
            modal.first._value, modal.second._value = '100' if index < 6 else '75', 'Quest' if index < 6 else 'Shop'
            current = event(1100 + index, user=9, permissions=('manage_messages',))
            current.guild.fetch_member.return_value = selected
            await modal.on_submit(current)
            modal.stop()
        assert bot.wallets.snapshot(100, wallet, 42)['balance'] == 525
        assert bot.wallets.snapshot(100, wallet, 9)['balance'] == 0
        await button(panel, 'History').callback(event(1200, user=9, permissions=('manage_messages',)))
        assert 'Page 1/2' in panel.embed().footer.text
        await button(panel, 'Next').callback(event(1201, user=9, permissions=('manage_messages',)))
        assert 'Page 2/2' in panel.embed().footer.text
        await button(panel, 'My balance').callback(event(1202, user=9, permissions=('manage_messages',)))
        assert panel.player.id == 9
        panel.stop()
        await bot.close()
    asyncio.run(check())


@pytest.mark.parametrize('case', ['other_user', 'other_server', 'lost_permission', 'expired', 'changed_player', 'changed_wallet', 'left_server', 'bot'])
def test_currency_forms_recheck_author_server_permission_target_and_expiry(case, make_engine):
    async def check():
        bot = DiceBot(make_engine())
        wallet = bot.wallets.save(1, 100, 'Avatar')['wallet']['id']
        second = bot.wallets.save(1, 100, 'Savings')['wallet']['id']
        panel = panel_for(bot, event(user=9, permissions=('manage_messages',)))
        panel.player = SimpleNamespace(id=42, display_name='Hero')
        modal = WalletInput(panel, 'add')
        modal.first._value, modal.second._value = '100', 'Quest'
        current = event(1001, user=9, permissions=('manage_messages',))
        current.guild.fetch_member.return_value = SimpleNamespace(id=42, bot=False)
        if case == 'other_user':
            current.user.id = 42
        elif case == 'other_server':
            current.guild_id = 200
        elif case == 'lost_permission':
            current.user.guild_permissions = discord.Permissions.none()
        elif case == 'expired':
            panel.stop()
        elif case == 'changed_player':
            panel.player = SimpleNamespace(id=99, display_name='Other')
        elif case == 'changed_wallet':
            panel.wallet_id = second
        elif case == 'left_server':
            current.guild.fetch_member.side_effect = discord.NotFound(SimpleNamespace(status=404, reason='Not Found'), 'Gone')
        else:
            current.guild.fetch_member.return_value.bot = True
        await modal.on_submit(current)
        assert bot.wallets.snapshot(100, wallet, 42)['balance'] == 0
        assert bot.wallets.snapshot(100, second, 42)['balance'] == 0
        messages = current.followup.send.await_args or current.response.send_message.await_args
        assert messages.kwargs['ephemeral']
        modal.stop()
        panel.stop()
        await bot.close()
    asyncio.run(check())


def test_noncreator_moderators_cannot_use_wallet_configuration_forms(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        wallet = bot.wallets.save(1, 100, 'Avatar')['wallet']['id']
        panel = panel_for(bot, event(user=9, permissions=('administrator',)))
        for kind in ('new', 'edit'):
            modal = WalletInput(panel, kind)
            modal.first._value, modal.second._value = 'Forged', 'gold'
            current = event(1001, user=9, permissions=('administrator',))
            await modal.on_submit(current)
            assert current.response.send_message.await_args.kwargs['ephemeral']
            modal.stop()
        assert bot.wallets.list(100) == [{'id': wallet, 'name': 'Avatar', 'currency': 'coins'}]
        panel.stop()
        await bot.close()
    asyncio.run(check())


def test_refresh_drops_other_player_view_when_moderator_permissions_are_revoked(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        wallet = bot.wallets.save(1, 100, 'Avatar')['wallet']['id']
        bot.wallets.change(9, 100, wallet, 42, 100, 'Reward', is_moderator=True)
        panel = panel_for(bot, event(user=9, permissions=('manage_messages',)))
        panel.player = SimpleNamespace(id=42, display_name='Hero')
        await button(panel, 'Refresh').callback(event(1001, user=9))
        assert panel.player.id == 9 and '**0 coins**' in panel.embed().description
        assert not any(isinstance(item, PlayerChoice) for item in panel.children)
        assert not any(getattr(item, 'label', None) == 'Add money' for item in panel.children)
        panel.stop()
        await bot.close()
    asyncio.run(check())


def test_wallet_options_cannot_select_a_foreign_server_wallet(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        local = bot.wallets.save(1, 100, 'Local')['wallet']['id']
        foreign = bot.wallets.save(1, 200, 'Foreign')['wallet']['id']
        panel = panel_for(bot, event())
        choice = next(item for item in panel.children if isinstance(item, WalletChoice))
        choice._values = [str(foreign)]
        current = event(1001)
        await choice.callback(current)
        assert panel.wallet_id == local
        assert current.followup.send.await_args.kwargs['ephemeral']
        panel.stop()
        await bot.close()
    asyncio.run(check())


def test_maximum_wallets_history_and_forms_fit_real_discord_payload_limits(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        for index in range(25):
            bot.wallets.save(1, 100, f'{index} ' + '*' * 28, '`' * 20)
        panel = panel_for(bot, event(user=1, permissions=('administrator',)))
        panel.player.display_name = '@everyone **' + '😀' * 100
        panel.guild_name = '@everyone **Server**'
        for index in range(7):
            bot.wallets.change(9, 100, panel.wallet_id, 1, 100, '@everyone ' + '*' * 110, is_moderator=True)
        panel.history = True
        panel.build_items()
        embed = panel.embed()
        assert len(embed) < 6000
        assert '@everyone' not in str(embed.to_dict())
        assert all(len(field.value) <= 1024 for field in embed.fields)
        rows = panel.to_components()
        assert len(rows) <= 5
        assert all(len(row['components']) <= 5 for row in rows)
        assert len({item.custom_id for item in panel.children}) == len(panel.children)
        choice = next(item for item in panel.children if isinstance(item, WalletChoice))
        assert len(choice.options) == 25
        for kind in ('new', 'edit', 'add', 'remove'):
            modal = WalletInput(panel, kind)
            payload = modal.to_dict()
            assert len(payload['title']) <= 45 and len(payload['components']) == 2
            assert all(label['component']['type'] == 4 for label in payload['components'])
            modal.stop()
        panel.stop()
        await bot.close()
    asyncio.run(check())


def test_closed_panel_disables_controls_without_losing_balances(make_engine):
    async def check():
        bot = DiceBot(make_engine())
        wallet = bot.wallets.save(1, 100, 'Avatar')['wallet']['id']
        bot.wallets.change(9, 100, wallet, 42, 100, 'Reward', is_moderator=True)
        panel = panel_for(bot, event())
        await panel.on_timeout()
        assert all(item.disabled for item in panel.children)
        assert bot.wallets.snapshot(100, wallet, 42)['balance'] == 100
        panel.stop()
        await bot.close()
    asyncio.run(check())
