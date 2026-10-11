"""Creator-only DM panel. Draft edits never arm a control until Apply is pressed."""

import logging
import secrets
import discord
from .controls import describe, empty_setting, panel_setting, player_id
from .display import safe
from .errors import RollError

log = logging.getLogger(__name__)
NO_MENTIONS = discord.AllowedMentions.none()

ROLLS = {
    'roll': ('/roll · Custom dice', 'Change the final total, including bonuses.'),
    'avatar': ('/avatar · Whole character', 'Good or bad luck on all applicable character rolls.'),
    'iq': ('/avatar · IQ', 'One d20: 1–20.'),
    'stats': ('/avatar · Six stats', 'Change the six-die total: 6–120.'),
    'nation': ('/avatar · Nation', 'Fire, Water, Earth, or Nomad.'),
    'tribe': ('/avatar · Water tribe', 'Southern, Northern, or Swamp; Water characters only.'),
    'family': ('/avatar · Fire family', 'Civilian, Military, High ranking, or Royal.'),
    'control': ('/avatar · Earth village', 'Whether the village is under Fire Nation control.'),
    'bending': ('/avatar · Bending check', '1–60 non-bender; 61–100 bender.'),
    'element': ('/avatar · Nomad element', 'Fire, Water, or Earth; bending must be above 60.'),
    'combat': ('/avatar · Non-bender combat', 'Sword, Bow, Fan, Fists, or Pressure point.'),
}
MODES = {
    'force': ('Force a result', 'Use once. Set an exact final total or choose an outcome.'),
    'shift': ('Add / subtract points', 'Use once. Enter +3, -2, or another whole number.'),
    'good': ('Good luck', 'Until off. Roll twice and keep the higher whole total.'),
    'bad': ('Bad luck', 'Until off. Roll twice and keep the lower whole total.'),
    'face': ('Text face', 'Use once. Choose an exact label from a custom /roll die.'),
}
PRESETS = {
    'nation': [('Fire Nation', 1), ('Water Tribes', 26), ('Earth Kingdom', 51), ('Nomad', 76)],
    'tribe': [('Southern tribe', 1), ('Northern tribe', 2), ('Swamp tribe', 3)],
    'family': [('Civilian family', 1), ('Military family', 50), ('High ranking family', 80), ('Royal family', 95)],
    'control': [('Under Fire Nation control', 1), ('Not under Fire Nation control', 16)],
    'bending': [('Bender', 61), ('Non-bender', 60)],
    'element': [('Fire bending', 1), ('Water bending', 2), ('Earth bending', 3)],
    'combat': [('Sword', 1), ('Bow', 21), ('Fan', 41), ('Fists', 61), ('Pressure point', 81)],
}
HELP = ('1. Choose the roll you want to change.\n'
        '2. Choose Force, Add/subtract, Good luck, Bad luck, or Text face.\n'
        '3. Choose player, or use Target me.\n'
        '4. Pick an outcome or Enter value, then press Apply.\n\n'
        'Only Apply changes live rolls. There is one active setting; Apply replaces it. '
        'Force, shifts, and text faces are used once. Luck stays on until Turn off. '
        'Player targets work in every server; no server ID is needed.\n\n'
        'Avatar controls apply to the selected part only. A /roll setting never changes '
        '/avatar. Six stats means their total, not each die. Whole character supports '
        'luck only. Higher/lower means the number, not which nation is best. '
        'A skipped one-use Avatar part clears after that player\'s character. '
        'For an impossible result, the normal roll is used and only you get the explanation.\n\n'
        'The Nomad element d3 runs only for Nomad characters with bending above 60. '
        'It never creates Air bending.\n\n'
        'To copy a player ID: Discord Settings → Advanced → Developer Mode, then '
        'right-click their profile → Copy User ID. '
        'After a restart or an expired panel, DM !rigger again.')


async def private_reply(interaction, text):
    if interaction.response.is_done():
        await interaction.followup.send(text, ephemeral=True, allowed_mentions=NO_MENTIONS)
    else:
        await interaction.response.send_message(text, ephemeral=True, allowed_mentions=NO_MENTIONS)


class PanelSelect(discord.ui.Select):
    def __init__(self, panel, kind, options, *, row, placeholder, disabled=False):
        self.panel, self.kind = panel, kind
        super().__init__(custom_id=panel.component_id(kind), options=options, row=row,
                         placeholder=placeholder, disabled=disabled)

    async def callback(self, interaction):
        if not await self.panel.authorize(interaction):
            return
        value = self.values[0]
        if self.kind == 'roll':
            if value not in ROLLS:
                await private_reply(interaction, 'Choose a roll from this panel.')
                return
            if value != self.panel.roll:
                self.panel.draft['value'] = None
            self.panel.roll = value
            self.panel.draft['scope'] = 'roll' if value == 'roll' else 'avatar'
            self.panel.draft['part'] = None if value in ('roll', 'avatar') else value
        elif self.kind == 'mode':
            if value not in MODES:
                await private_reply(interaction, 'Choose a mode from this panel.')
                return
            if value != self.panel.draft['mode']:
                self.panel.draft['value'] = None
            self.panel.draft['mode'] = value
        else:
            presets = {str(number) for _, number in PRESETS.get(self.panel.roll, [])}
            if self.panel.draft['mode'] != 'force' or value not in presets:
                await private_reply(interaction, 'Choose an outcome for the currently selected roll.')
                return
            self.panel.draft['value'] = int(value)
        self.panel.note = 'Draft updated. Press Apply when ready.'
        await self.panel.update(interaction)


class PanelInput(discord.ui.Modal):
    def __init__(self, panel, kind):
        self.panel, self.kind = panel, kind
        self.mode, self.roll = panel.draft['mode'], panel.roll
        super().__init__(title='Choose player' if kind == 'target' else 'Enter value', timeout=180)
        current = panel.draft['target' if kind == 'target' else 'value']
        self.field = discord.ui.TextInput(
            default=str(current) if current is not None else None,
            placeholder='Paste their user ID or mention' if kind == 'target' else
                        'Exact face label' if self.mode == 'face' else 'Whole number, such as 15 or -2',
            min_length=1, max_length=40)
        self.add_item(discord.ui.Label(text='Player user ID or mention' if kind == 'target' else 'Value',
                                      component=self.field))

    async def interaction_check(self, interaction):
        return await self.panel.authorize(interaction)

    async def on_submit(self, interaction):
        # Recheck at submission as well as dispatch; the panel may have expired.
        if not await self.panel.authorize(interaction):
            return
        try:
            if self.kind == 'target':
                target = player_id(self.field.value)
                await interaction.response.defer()
                try:
                    user = self.panel.bot.get_user(int(target)) or await self.panel.bot.fetch_user(int(target))
                except discord.NotFound:
                    raise RollError('That user was not found. Copy the player\'s user ID, not a server or application ID.')
                except discord.HTTPException:
                    raise RollError('Could not check that player. Try Choose player again.')
                if user.bot:
                    raise RollError('Choose a player account, not a bot account.')
                if self.panel.is_finished():
                    raise RollError('This panel has closed. DM !rigger to open a new one.')
                self.panel.draft['target'] = target
            else:
                if self.mode != self.panel.draft['mode'] or self.roll != self.panel.roll:
                    raise RollError('The selected roll or mode changed. Open Enter value again.')
                draft = {**self.panel.draft, 'value': self.field.value}
                new = panel_setting(**draft)
                self.panel.draft['value'] = new['value']
            self.panel.note = 'Draft updated. Press Apply when ready.'
            await self.panel.update(interaction)
        except RollError as exc:
            await private_reply(interaction, '⚠️ ' + safe(exc))

    async def on_error(self, interaction, error):
        log.warning('Private panel input failed: %s.', type(error).__name__)
        await private_reply(interaction, 'Could not update the draft. Open !rigger again.')


class RiggerPanel(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=600)
        self.bot, self.message = bot, None
        self.nonce = secrets.token_hex(6)
        active = bot.engine.control_status(bot.engine.owner_id, is_dm=True)
        if active['mode'] == 'off':
            self.draft = {'mode': 'force', 'value': None, 'target': str(bot.engine.owner_id),
                          'scope': 'roll', 'part': None}
        else:
            self.draft = {key: active[key] for key in ('mode', 'value', 'target', 'scope', 'part')}
            # Legacy unrestricted rules stay active until Apply or Turn off.
            # New panel rules always have an explicit command scope.
            if self.draft['scope'] == 'all':
                self.draft['scope'] = 'avatar' if self.draft['part'] else 'roll'
            if self.draft['target'] is None:
                self.draft['target'] = str(bot.engine.owner_id)
        self.roll = self.draft['part'] or self.draft['scope']
        self.note = 'Choose player, roll, and outcome. Press Apply to arm it.'
        self.build_items()

    def component_id(self, key):
        return f'rigger:{self.nonce}:{key}'

    async def authorize(self, interaction):
        if interaction.user.id != self.bot.engine.owner_id or interaction.guild_id is not None:
            await private_reply(interaction, 'These controls are private to the bot creator.')
            return False
        if self.is_finished():
            await private_reply(interaction, 'This panel has closed. DM !rigger to open a new one.')
            return False
        return True

    async def interaction_check(self, interaction):
        return await self.authorize(interaction)

    def build_items(self):
        self.clear_items()
        self.add_item(PanelSelect(self, 'roll', [discord.SelectOption(label=label, value=key,
            description=hint, default=key == self.roll) for key, (label, hint) in ROLLS.items()],
            row=0, placeholder='Choose the roll'))
        self.add_item(PanelSelect(self, 'mode', [discord.SelectOption(label=label, value=key,
            description=hint, default=key == self.draft['mode']) for key, (label, hint) in MODES.items()],
            row=1, placeholder='Choose what to change'))
        quick = PRESETS.get(self.roll, []) if self.draft['mode'] == 'force' else []
        options = [discord.SelectOption(label=label, value=str(value), description=f'Forces the die to {value}.',
                   default=value == self.draft['value']) for label, value in quick]
        self.add_item(PanelSelect(self, 'outcome', options or [discord.SelectOption(label='Use Enter value', value='none')],
                      row=2, placeholder='Pick an outcome' if quick else 'Use Enter value, or choose a luck mode', disabled=not quick))
        for label, key, handler, row, style in [
            ('Choose player', 'target', self.choose_target, 3, discord.ButtonStyle.secondary),
            ('Target me', 'me', self.target_me, 3, discord.ButtonStyle.secondary),
            ('Enter value', 'value', self.choose_value, 3, discord.ButtonStyle.secondary),
            ('Apply', 'apply', self.apply, 4, discord.ButtonStyle.success),
            ('Turn off', 'off', self.turn_off, 4, discord.ButtonStyle.danger),
            ('Refresh', 'refresh', self.refresh, 4, discord.ButtonStyle.secondary),
            ('Help', 'help', self.help, 4, discord.ButtonStyle.secondary),
        ]:
            button = discord.ui.Button(label=label, custom_id=self.component_id(key), row=row, style=style,
                                       disabled=key == 'value' and self.draft['mode'] in ('good', 'bad'))
            async def callback(interaction, handler=handler):
                if await self.authorize(interaction):
                    await handler(interaction)
            button.callback = callback
            self.add_item(button)

    def embed(self):
        active = self.bot.engine.control_status(self.bot.engine.owner_id, is_dm=True)
        embed = discord.Embed(title='🎲 Rigger', description=self.note, colour=0x5865F2)
        target = self.draft['target']
        embed.add_field(name='Player', value=f"{'You' if target == str(self.bot.engine.owner_id) else 'Player'} · `{target}`", inline=False)
        embed.add_field(name='Roll', value=ROLLS[self.roll][0], inline=True)
        embed.add_field(name='Change', value=MODES[self.draft['mode']][0], inline=True)
        value = self.draft['value']
        embed.add_field(name='Value', value='No value needed' if self.draft['mode'] in ('good', 'bad') else
                        safe(value) if value is not None else 'Pick an outcome or Enter value', inline=False)
        embed.add_field(name='Active setting', value=safe(describe(active)), inline=False)
        if active['last']:
            embed.add_field(name='Last affected roll', value=safe(active['last'])[:1024], inline=False)
        embed.set_footer(text='Private to you • Apply saves • One active setting • Force/shift once; luck until off')
        return embed

    async def update(self, interaction):
        self.build_items()
        if interaction.response.is_done():
            await self.message.edit(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)
        else:
            await interaction.response.edit_message(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)

    async def choose_target(self, interaction):
        await interaction.response.send_modal(PanelInput(self, 'target'))

    async def choose_value(self, interaction):
        await interaction.response.send_modal(PanelInput(self, 'value'))

    async def target_me(self, interaction):
        self.draft['target'] = str(self.bot.engine.owner_id)
        self.note = 'Draft targets you. Press Apply when ready.'
        await self.update(interaction)

    async def apply(self, interaction):
        await interaction.response.defer()
        try:
            self.bot.engine.configure(interaction.user.id, is_dm=interaction.guild_id is None,
                                      request_id=interaction.id, **self.draft)
        except RollError as exc:
            await private_reply(interaction, '⚠️ ' + safe(exc))
            return
        self.note = '✅ Setting armed. Only matching rolls from the selected player will use it.'
        await self.update(interaction)

    async def turn_off(self, interaction):
        await interaction.response.defer()
        self.bot.engine.configure(interaction.user.id, is_dm=interaction.guild_id is None,
                                  mode='off', request_id=interaction.id)
        self.note = '✅ Rigger is off. Your draft is kept below for editing.'
        await self.update(interaction)

    async def refresh(self, interaction):
        self.note = 'Active setting refreshed. Draft changes still need Apply.'
        await self.update(interaction)

    async def help(self, interaction):
        await private_reply(interaction, HELP)

    async def refresh_message(self):
        if self.message is not None and not self.is_finished():
            await self.message.edit(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)

    async def expire(self):
        self.stop()
        for item in self.children:
            item.disabled = True
        self.note = 'Panel closed. DM !rigger to reopen it. Active settings are kept.'
        if self.message is not None:
            try:
                await self.message.edit(embed=self.embed(), view=self, allowed_mentions=NO_MENTIONS)
            except discord.HTTPException:
                pass

    async def on_timeout(self):
        await self.expire()

    async def on_error(self, interaction, error, item):
        log.warning('Private panel action failed: %s.', type(error).__name__)
        await private_reply(interaction, 'Could not update the setting. Press Refresh or DM !rigger again.')
