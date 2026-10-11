"""Validated private controls and the internal legacy-command adapter."""

import re
import shlex
from .avatar import PART_DICE, PART_LIMITS
from .errors import RollError, require

HELP = ('DM !rigger to use the private panel. Choose a player and roll, then Apply. '
        'Use Luck % for 1–100% strength, Stat 1–6 for individual dice, and Active rigs '
        'to check or remove saved controls. Live DMs do not execute command arguments.')

MAX_VALUE = 200_000_000_000
MAX_RIGS = 100
TARGET = re.compile(r'(?:<@!?(\d+)>|(\d+))\Z')
NUMBER = re.compile(r'[+-]?\d+\Z')
COMMAND = re.compile(r'!rigger(?:\s|$)', re.IGNORECASE)


def empty_setting():
    return {'mode': 'off', 'value': None, 'target': None, 'part': None, 'scope': 'roll', 'last': None}


def player_id(value):
    """Accept a copied user ID or mention without depending on a guild cache."""
    match = TARGET.fullmatch(str(value).strip())
    require(match and 0 < int(match[1] or match[2]) < 2**64,
            'Paste a Discord user ID or mention. Right-click the player and choose Copy User ID.')
    return str(int(match[1] or match[2]))


def panel_setting(mode, value=None, target=None, *, scope='roll', part=None):
    """Validate a panel draft before changing the active setting."""
    require(mode in ('off', 'force', 'shift', 'good', 'bad', 'face'), 'Choose a control mode.')
    if mode == 'off':
        return empty_setting()
    require(scope in ('roll', 'avatar'), 'Choose /roll or an Avatar roll.')
    require(part is None or part in PART_DICE, 'Choose an Avatar roll.')
    require(scope != 'roll' or part is None, 'Avatar parts only work on /avatar.')
    require(scope != 'avatar' or part is not None or mode in ('good', 'bad'),
            'Whole-character controls support luck. Choose a specific Avatar part to force or shift it.')
    require(part != 'stats' or mode in ('good', 'bad'),
            'Choose Stat 1–6 to force or shift an individual die. Six stats supports luck.')
    target = None if target is None else player_id(target)
    if mode in ('force', 'shift'):
        require(isinstance(value, (str, int)) and not isinstance(value, bool)
                and len(str(value)) <= 30 and NUMBER.fullmatch(str(value).strip()),
                'Enter a whole number using Enter value.')
        value = int(str(value).strip())
        require(abs(value) <= MAX_VALUE, 'Use a value within ±200 billion.')
        if part is not None and mode == 'force':
            low, high = PART_LIMITS[part]
            require(low <= value <= high, f'For {part}, choose a value from {low} to {high}.')
    elif mode == 'face':
        require(scope == 'roll', 'Text faces only work with /roll custom dice.')
        require(isinstance(value, str) and 1 <= len(value) <= 40 and not any(ord(c) < 32 for c in value),
                'Enter the exact text face, using 1–40 characters.')
    else:
        value = 100 if value is None else value
        text = str(value).strip().removesuffix('%').strip()
        require(isinstance(value, (str, int)) and not isinstance(value, bool)
                and len(str(value)) <= 8 and NUMBER.fullmatch(text),
                'Enter a whole luck strength from 1 to 100.')
        value = int(text)
        require(1 <= value <= 100, 'Luck strength must be 1–100%. Use Remove selected to turn it off.')
    return {'mode': mode, 'value': value, 'target': target, 'part': part, 'scope': scope, 'last': None}


def parse_command(content):
    require(isinstance(content, str) and len(content) <= 500, 'Keep the command under 500 characters.')
    try:
        words = shlex.split(content)
    except ValueError as exc:
        raise RollError('Close your quotation marks. Example: !Rigger face "heavy rain".') from exc
    args = words[1:]
    if not args:
        return 'help', None
    first = args.pop(0).lower()
    part = None
    if first == 'avatar':
        require(args, 'Choose an Avatar part. Example: !Rigger avatar nation 30.')
        first = args.pop(0).lower()
        require(first in PART_DICE, 'Choose: iq, stats, nation, tribe, family, control, bending, element, or combat.')
    if first in PART_DICE:
        part = first
        require(args, f'Give a number, shift, good, or bad. Example: !Rigger {part} 10.')
        first = args.pop(0).lower()
    if first in ('help', 'status', 'off'):
        require(part is None, f'Use !Rigger {first} by itself.')
        require(not args, f'Use !Rigger {first} by itself.')
        return first, None
    if first in ('force', 'shift', 'face', 'luck'):
        require(args, 'Give a value. Examples: !Rigger 15, !Rigger +3, !Rigger good.')
        value = args.pop(0)
        mode = first
        if first == 'luck':
            mode, value = value.lower(), None
            require(mode in ('good', 'bad'), 'Use !Rigger good or !Rigger bad.')
    elif first in ('good', 'bad'):
        mode, value = first, None
    elif NUMBER.fullmatch(first):
        mode, value = ('shift' if first.startswith(('+', '-')) else 'force'), first
    else:
        raise RollError('Use !Rigger 15, !Rigger +3, !Rigger good, !Rigger bad, or !Rigger off. See !Rigger help.')
    if mode in ('force', 'shift'):
        require(isinstance(value, str) and NUMBER.fullmatch(value), 'Use a whole number, such as 15 or -2.')
        value = int(value)
        require(abs(value) <= MAX_VALUE, 'That number is too large; use a value within ±200 billion.')
    if mode == 'face':
        require(part is None, 'Avatar dice are numeric. Use a number, shift, good, or bad.')
        require(1 <= len(value) <= 40 and not any(ord(c) < 32 for c in value), 'Use a text face of 1–40 characters, with quotes for spaces.')
    if part is not None and mode == 'force':
        low, high = PART_LIMITS[part]
        require(low <= value <= high, f'For {part}, force a total from {low} to {high}.')
    require(len(args) <= 1, 'Give only one optional target: @User or their user ID.')
    target = None
    if args:
        match = TARGET.fullmatch(args[0])
        require(match and 0 < int(match[1] or match[2]) < 2**64, 'The target must be @User or a positive Discord user ID.')
        target = str(int(match[1] or match[2]))
    return 'set', {'mode': mode, 'value': value, 'target': target, 'part': part,
                   'scope': 'avatar' if part else 'all', 'last': None}


def describe(setting):
    mode, value = setting['mode'], setting['value']
    if mode == 'off':
        return 'Rigger is off. Rolls are normal.'
    label = {'force': f'Next final total: {value}', 'shift': f'Next total shift: {value:+d}' if mode == 'shift' else '',
             'face': f'Next text face: {value}', 'good': f'Good luck: {value or 100}% until removed',
             'bad': f'Bad luck: {value or 100}% until removed'}[mode]
    scope = (f"\nRoll: /avatar {setting['part']} only." if setting.get('part') else
             '\nRoll: all /avatar parts.' if setting.get('scope') == 'avatar' else
             '\nRoll: /roll only.' if setting.get('scope') == 'roll' else '\nRoll: /roll and /avatar (legacy setting).')
    return label + scope + '\nTarget: ' + (f"user {setting['target']} in every server." if setting['target'] else 'anyone in any server.')


def empty_controls():
    return {'rules': [], 'next_id': 1, 'last': None}


def category(rule):
    return 'luck' if rule['mode'] in ('good', 'bad') else rule['mode']


def rule_key(rule):
    """Applying a draft replaces only the same player's slot and kind."""
    return rule['target'], rule['scope'], rule['part'], category(rule)
