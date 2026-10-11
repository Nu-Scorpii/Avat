"""Creator-only DM panel. Draft edits never arm a control until Apply is pressed."""

import logging
import secrets
import discord
from .controls import category, panel_setting, player_id
from .display import chunks, safe
from .errors import RollError

log = logging.getLogger(__name__)
NO_MENTIONS = discord.AllowedMentions.none()

ROLLS = {
    'roll': ('/roll · Custom dice', 'Change the final total, including bonuses.'),
    'avatar': ('/avatar · Whole character', 'Good or bad luck on all applicable character rolls.'),
    'iq': ('/avatar · IQ', 'One d20: 1–20.'),
    'stats': ('/avatar · All six stats', 'Luck on all six dice. Use Stat 1–6 for exact results.'),
    **{f'stat{index}': (f'/avatar · Stat {index}', f'Change only die {index} of the ordered 6d20 roll: 1–20.')
       for index in range(1, 7)},
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
    'good': ('Good luck', '1–100% strength toward the highest legal result. Lasts until removed.'),
    'bad': ('Bad luck', '1–100% strength toward the lowest legal result. Lasts until removed.'),
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
        'Only Apply changes live rolls. Add several Avatar rigs for the same player. '
        'Apply replaces only the same player + roll + kind; other rigs stay active. '
        'Good/bad share one luck slot. Force, shifts, and text faces are used once. '
        'Luck stays on until removed. Active rigs lists every saved rig, with player filtering, '
        'Edit selected, Remove selected, Clear player, and Clear all. '
        'Player targets work in every server; no server ID is needed.\n\n'
        'Luck strength is 1–100%, not a chance to activate. Each numeric die moves that '
        'fraction toward its best/worst face, rounded to a legal face. 50% moves halfway; '
        '100% reaches the extreme. Very small strengths may round to no change. '
        'Signed dice respect the final total. Text dice skip luck.\n\n'
        'Choose Stat 1–6 to force or shift each of the six d20s separately. All six stats '
        'and Whole character support luck only. A stat-specific luck overrides all-stats '
        'luck, which overrides whole-character luck. Luck, then shift, then exact force '
        'runs on each part; force wins. Higher/lower means the number, not which nation is best. '
        'A /roll setting never changes /avatar. '
        'A skipped one-use Avatar part clears after that player\'s character. '
        'For an impossible result, the normal roll is used and only you get the explanation.\n\n'
        'The Nomad element d3 runs only for Nomad characters with bending above 60. '
        'It never creates Air bending.\n\n'
        'To copy a player ID: Discord Settings → Advanced → Developer Mode, then '
        'right-click their profile → Copy User ID. '
        'After a restart or an expired panel, DM !rigger again.')
PAGE_SIZE = 8


def roll_label(rule):
    key = rule['part'] or rule['scope']
    return ROLLS.get(key, ('Legacy /roll + /avatar', ''))[0]


def change_label(rule):
    mode, value = rule['mode'], rule['value']
    if mode in ('good', 'bad'):
        return f"{'Good' if mode == 'good' else 'Bad'} luck {value}% · until removed"
    if mode == 'shift':
        return f'Shift {value:+d} · once'
    return f"{'Force' if mode == 'force' else 'Text face'} {value} · once"


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
            if self.panel.draft['mode'] not in self.panel.allowed_modes():
                self.panel.draft.update(mode='good', value=50)
            elif self.panel.draft['mode'] in ('good', 'bad') and self.panel.draft['value'] is None:
                self.panel.draft['value'] = 50
        elif self.kind == 'mode':
            if value not in self.panel.allowed_modes():
                await private_reply(interaction, 'Choose a mode from this panel.')
                return
            if value != self.panel.draft['mode']:
                old_luck = self.panel.draft['mode'] in ('good', 'bad')
                self.panel.draft['value'] = (self.panel.draft['value'] if old_luck else 50) if value in ('good', 'bad') else None
            self.panel.draft['mode'] = value
        elif self.kind == 'active':
            active = self.panel.bot.engine.control_status(interaction.user.id, is_dm=True)
            if not value.isdecimal() or not any(r['id'] == int(value) for r in active['rules']):
                await private_reply(interaction, 'That rig has already been used or removed. Press Refresh.')
                return
            self.panel.selected_id = int(value)
            self.panel.note = 'Selected rig. Edit it or remove only this rig.'
            await self.panel.update(interaction)
            return
        else:
            presets = {str(number) for _, number in self.panel.quick_choices()}
            if value not in presets:
                await private_reply(interaction, 'Choose an outcome for the currently selected roll.')
                return
            self.panel.draft['value'] = int(value)
        self.panel.note = 'Draft updated. Press Apply when ready.'
        await self.panel.update(interaction)


class PanelInput(discord.ui.Modal):
    def __init__(self, panel, kind):
        self.panel, self.kind = panel, kind
        self.mode, self.roll = panel.draft['mode'], panel.roll
        self.target = panel.draft['target']
        luck = self.mode in ('good', 'bad')
        super().__init__(title='Choose player' if kind == 'target' else 'Luck strength' if luck else 'Enter value', timeout=180)
        current = panel.draft['target' if kind == 'target' else 'value']
        self.field = discord.ui.TextInput(
            default=str(current) if current is not None else None,
            placeholder='Paste their user ID or mention' if kind == 'target' else
                        '1–100, such as 50' if luck else
                        'Exact face label' if self.mode == 'face' else 'Whole number, such as 15 or -2',
            min_length=1, max_length=40)
        self.add_item(discord.ui.Label(text='Player user ID or mention' if kind == 'target' else 'Strength (%)' if luck else 'Value',
                                      component=self.field))

    async def interaction_check(self, interaction):
        return await self.panel.authorize(interaction)

    async def on_submit(self, interaction):
        # Recheck at submission as well as dispatch; the panel may have expired.
        if not await self.panel.authorize(interaction):
            return
        try:
            if self.panel.page != 'edit' or self.target != self.panel.draft['target']:
                raise RollError('The panel or player changed. Open the form again.')
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
        self.page, self.active_page, self.selected_id, self.player_only = 'edit', 0, None, False
        if not active['rules']:
            self.draft = {'mode': 'force', 'value': None, 'target': str(bot.engine.owner_id),
                          'scope': 'roll', 'part': None}
        else:
            recent = active['rules'][-1]
            self.draft = {key: recent[key] for key in ('mode', 'value', 'target', 'scope', 'part')}
            # Legacy unrestricted rules stay active until Apply or Turn off.
            # New panel rules always have an explicit command scope.
            if self.draft['scope'] == 'all':
                self.draft['scope'] = 'avatar' if self.draft['part'] else 'roll'
            if self.draft['target'] is None:
                self.draft['target'] = str(bot.engine.owner_id)
            if self.draft['part'] == 'stats' and self.draft['mode'] not in ('good', 'bad'):
                self.draft.update(mode='good', value=50)
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
        if self.page == 'active':
            self.build_active_items()
            return
        self.add_item(PanelSelect(self, 'roll', [discord.SelectOption(label=label, value=key,
            description=hint, default=key == self.roll) for key, (label, hint) in ROLLS.items()],
            row=0, placeholder='Choose the roll'))
        self.add_item(PanelSelect(self, 'mode', [discord.SelectOption(label=label, value=key,
            description=hint, default=key == self.draft['mode']) for key, (label, hint) in MODES.items()
            if key in self.allowed_modes()],
            row=1, placeholder='Choose what to change'))
        quick = self.quick_choices()
        options = [discord.SelectOption(label=label, value=str(value), description=
                   f'Luck strength {value}%.' if self.draft['mode'] in ('good', 'bad') else f'Forces the die to {value}.',
                   default=value == self.draft['value']) for label, value in quick]
        self.add_item(PanelSelect(self, 'outcome', options or [discord.SelectOption(label='Use Enter value', value='none')],
                      row=2, placeholder='Pick strength or outcome' if quick else 'Use Enter value', disabled=not quick))
        for label, key, handler, row, style in [
            ('Choose player', 'target', self.choose_target, 3, discord.ButtonStyle.secondary),
            ('Target me', 'me', self.target_me, 3, discord.ButtonStyle.secondary),
            ('Luck %' if self.draft['mode'] in ('good', 'bad') else 'Enter value', 'value', self.choose_value, 3, discord.ButtonStyle.secondary),
            ('Apply', 'apply', self.apply, 4, discord.ButtonStyle.success),
            ('Active rigs', 'active_page', self.show_active, 4, discord.ButtonStyle.primary),
            ('Clear all', 'off', self.turn_off, 4, discord.ButtonStyle.danger),
            ('Refresh', 'refresh', self.refresh, 4, discord.ButtonStyle.secondary),
            ('Help', 'help', self.help, 4, discord.ButtonStyle.secondary),
        ]:
            self.add_button(label, key, handler, row, style)

    def allowed_modes(self):
        return ('good', 'bad') if self.roll in ('avatar', 'stats') else tuple(
            mode for mode in MODES if mode != 'face' or self.roll == 'roll')

    def quick_choices(self):
        if self.draft['mode'] in ('good', 'bad'):
            return [(f'{percent}% strength', percent) for percent in (1, 25, 50, 75, 100)]
        return PRESETS.get(self.roll, []) if self.draft['mode'] == 'force' else []

    def add_button(self, label, key, handler, row, style=discord.ButtonStyle.secondary, *, disabled=False):
        item = discord.ui.Button(label=label, custom_id=self.component_id(key), row=row, style=style, disabled=disabled)
        async def callback(interaction):
            if await self.authorize(interaction):
                await handler(interaction)
        item.callback = callback
        self.add_item(item)

    def active_slice(self, active):
        rules = [r for r in active['rules'] if not self.player_only or r['target'] == self.draft['target']]
        self.active_page = min(self.active_page, max(0, (len(rules) - 1) // PAGE_SIZE))
        if not any(r['id'] == self.selected_id for r in rules):
            self.selected_id = None
        return rules, rules[self.active_page * PAGE_SIZE:(self.active_page + 1) * PAGE_SIZE]

    def build_active_items(self):
        active = self.bot.engine.control_status(self.bot.engine.owner_id, is_dm=True)
        rules, shown = self.active_slice(active)
        options = [discord.SelectOption(label=f"#{r['id']} · {roll_label(r)} · {change_label(r)}"[:100],
                   value=str(r['id']), description=f"Player {r['target'] or 'anyone (legacy)'}",
                   default=r['id'] == self.selected_id) for r in shown]
        self.add_item(PanelSelect(self, 'active', options or [discord.SelectOption(label='No active rigs', value='none')],
                      row=0, placeholder='Choose a rig to edit or remove', disabled=not shown))
        for label, key, handler, row, style, disabled in [
            ('Edit selected', 'edit', self.edit_selected, 1, discord.ButtonStyle.primary, self.selected_id is None),
            ('Remove selected', 'remove', self.remove_selected, 1, discord.ButtonStyle.danger, self.selected_id is None),
            ('Clear player', 'clear_player', self.clear_player, 1, discord.ButtonStyle.danger, False),
            ('Clear all', 'off', self.turn_off, 1, discord.ButtonStyle.danger, not active['rules']),
            ('Previous', 'prev', self.previous_page, 2, discord.ButtonStyle.secondary, self.active_page == 0),
            ('Next', 'next', self.next_page, 2, discord.ButtonStyle.secondary, (self.active_page + 1) * PAGE_SIZE >= len(rules)),
            ('Show all players' if self.player_only else 'Only chosen player', 'filter', self.toggle_filter, 2, discord.ButtonStyle.secondary, False),
            ('Back to draft', 'back', self.back_to_draft, 3, discord.ButtonStyle.secondary, False),
            ('Refresh', 'refresh', self.refresh, 3, discord.ButtonStyle.secondary, False),
            ('Help', 'help', self.help, 3, discord.ButtonStyle.secondary, False),
        ]:
            self.add_button(label, key, handler, row, style, disabled=disabled)

    def embed(self):
        active = self.bot.engine.control_status(self.bot.engine.owner_id, is_dm=True)
        if self.page == 'active':
            rules, shown = self.active_slice(active)
            embed = discord.Embed(title=f"🔒 Active rigs · {len(active['rules'])}", description=self.note, colour=0x5865F2)
            embed.add_field(name='Chosen player · Clear player affects this ID', value=f"`{self.draft['target']}`", inline=False)
            for rule in shown:
                embed.add_field(name=f"#{rule['id']} · {roll_label(rule)}", value=safe(
                    f"Player {rule['target'] or 'anyone (legacy)'}\n{change_label(rule)}"), inline=False)
            if not shown:
                embed.add_field(name='Status', value='No active rigs in this view.', inline=False)
            if active['last']:
                embed.add_field(name='Last affected roll', value=safe(active['last'])[:1024], inline=False)
            embed.set_footer(text=f"Page {self.active_page + 1}/{max(1, (len(rules) + PAGE_SIZE - 1) // PAGE_SIZE)} • "
                             f"{'Chosen player' if self.player_only else 'All players'} • Private to you")
            return embed
        embed = discord.Embed(title='🎲 Rigger', description=self.note, colour=0x5865F2)
        target = self.draft['target']
        embed.add_field(name='Player', value=f"{'You' if target == str(self.bot.engine.owner_id) else 'Player'} · `{target}`", inline=False)
        embed.add_field(name='Roll', value=ROLLS[self.roll][0], inline=True)
        embed.add_field(name='Change', value=MODES[self.draft['mode']][0], inline=True)
        value = self.draft['value']
        embed.add_field(name='Strength' if self.draft['mode'] in ('good', 'bad') else 'Value',
                        value=f'{value}%' if self.draft['mode'] in ('good', 'bad') else
                        safe(value) if value is not None else 'Pick an outcome or Enter value', inline=False)
        player_rules = [r for r in active['rules'] if r['target'] == target]
        brief = [f"#{r['id']} · {roll_label(r)} · {change_label(r)}" for r in player_rules[:4]]
        embed.add_field(name=f"Active rigs · {len(active['rules'])} total / {len(player_rules)} for this player",
                        value=safe('\n'.join(brief))[:900] + ('\nOpen Active rigs to see the full list.' if player_rules else
                              'No rigs for this player. Open Active rigs to check everyone.'), inline=False)
        if active['last']:
            embed.add_field(name='Last affected roll', value=safe(active['last'])[:1024], inline=False)
        embed.set_footer(text='Private to you • Apply adds or updates one rig • Force/shift once; luck until removed')
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
            active = self.bot.engine.configure(interaction.user.id, is_dm=interaction.guild_id is None,
                                              request_id=interaction.id, **self.draft)
        except RollError as exc:
            await private_reply(interaction, '⚠️ ' + safe(exc))
            return
        self.note = f"✅ Rig saved · {len(active['rules'])} active. Other rigs were kept. Only matching player rolls use it."
        await self.update(interaction)

    async def turn_off(self, interaction):
        await interaction.response.defer()
        self.bot.engine.configure(interaction.user.id, is_dm=interaction.guild_id is None,
                                  mode='off', request_id=interaction.id)
        self.selected_id = None
        self.note = '✅ All rigs cleared. Your draft is kept for editing.'
        await self.update(interaction)

    async def refresh(self, interaction):
        self.note = 'Active rigs refreshed. Draft changes still need Apply.'
        await self.update(interaction)

    async def show_active(self, interaction):
        self.page, self.active_page, self.player_only = 'active', 0, False
        self.note = 'All active rigs. Select one to edit or remove; use the filter to check your chosen player.'
        await self.update(interaction)

    async def back_to_draft(self, interaction):
        self.page = 'edit'
        self.note = 'Draft kept. Press Apply to save one rig.'
        await self.update(interaction)

    async def toggle_filter(self, interaction):
        self.player_only = not self.player_only
        self.active_page = 0
        await self.update(interaction)

    async def previous_page(self, interaction):
        self.active_page = max(0, self.active_page - 1)
        await self.update(interaction)

    async def next_page(self, interaction):
        self.active_page += 1
        await self.update(interaction)

    async def edit_selected(self, interaction):
        active = self.bot.engine.control_status(interaction.user.id, is_dm=interaction.guild_id is None)
        rule = next((r for r in active['rules'] if r['id'] == self.selected_id), None)
        if rule is None:
            await private_reply(interaction, 'That rig has already been used or removed. Press Refresh.')
            return
        if rule['scope'] == 'all' or rule['part'] == 'stats' and category(rule) != 'luck':
            await private_reply(interaction, 'This is a legacy rig. Remove it and create an explicit /roll or Avatar rig.')
            return
        self.draft = {key: rule[key] for key in ('mode', 'value', 'target', 'scope', 'part')}
        self.draft['target'] = self.draft['target'] or str(self.bot.engine.owner_id)
        self.roll = self.draft['part'] or self.draft['scope']
        self.page = 'edit'
        self.note = f"Editing rig #{rule['id']}. Apply updates this slot; changing player/roll/kind creates another rig."
        await self.update(interaction)

    async def remove_selected(self, interaction):
        await interaction.response.defer()
        if self.selected_id is not None:
            self.bot.engine.remove_control(interaction.user.id, is_dm=interaction.guild_id is None,
                                           rule_id=self.selected_id, request_id=interaction.id)
        self.selected_id = None
        self.note = '✅ Selected rig removed. Other rigs were kept.'
        await self.update(interaction)

    async def clear_player(self, interaction):
        await interaction.response.defer()
        self.bot.engine.remove_control(interaction.user.id, is_dm=interaction.guild_id is None,
                                       target=self.draft['target'], request_id=interaction.id)
        self.note = f"✅ Cleared rigs for player {self.draft['target']}. Other players' rigs were kept."
        await self.update(interaction)

    async def help(self, interaction):
        for part in chunks(HELP, 1900):
            await private_reply(interaction, part)

    async def refresh_message(self):
        if self.message is not None and not self.is_finished():
            self.build_items()
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
