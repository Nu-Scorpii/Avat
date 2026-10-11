# Simple Discord Dice Bot · 3.2.0

Two public commands: `/roll` for custom dice and `/avatar` for Avatar character creation. Creator controls work privately in DMs. No character tracking, battles, attendance, or saved-die menus.

## Players: `/roll`

Type `/roll` for **1d20**. Every option is optional.

| Option | What to put in it |
|---|---|
| `dice` | `1d20`, `2d17+1d8-3`, or `2d[custom]` |
| `bonus` | Extra points, such as `3` or `-2` |
| `faces` | A JSON list such as `[0,1,1,5]` or `["sun","rain","rain","storm"]` |
| `keep` | All dice, Highest die, or Lowest die |

Examples:

```text
/roll
/roll dice:1d20 bonus:3
/roll dice:2d17+1d8-3
/roll dice:2d20 keep:Highest die bonus:2
/roll faces:[0,1,1,5]
/roll dice:3d[custom] faces:[0,1,1,5] bonus:2
/roll faces:["sun","rain","rain","storm"]
```

Select the option values in Discord; the examples show what goes into each field. When `dice` is omitted and `faces` is provided, the bot automatically rolls one of your custom dice. Faces belong to that command only. Repeat a face to make it more likely. To mix several custom dice, use `dice:1d[a]+1d[b]` with `faces:{"a":[0,3,8],"b":[1,2,5]}`.

Numeric results add signed modifiers and `bonus` once, after any highest/lowest selection. Highest/lowest works with one positive pool, such as `3d20+2`. A die containing any text face always has no total and cannot use arithmetic, bonuses, or highest/lowest. Text face spelling and capitalization are preserved.

Messages stay short:

```text
🎲 Hero rolled 1d20

Rolls: 8
Bonus: +3

Total: 11
```

Dice values use code formatting and the heading and total are bold. Long rolls are split into readable messages. Input mistakes receive private errors.

Limits: 100 dice per roll, 1–1 billion sides, up to 20 expression terms, 1–1,000 faces per custom die, and whole-number bonuses/modifiers within ±1 billion. Text faces may contain 1–40 characters. No programming expressions are evaluated.

## Players: `/avatar`

Run `/avatar` in a server. There are no options to fill in. The bot rolls the whole character in this order:

1. **IQ:** 1d20.
2. **Stats:** six separate results from 6d20, in order. Assign your own stat names; the bot does not invent them.
3. **Nation:** 1d100, followed by its applicable origin detail.
4. **Bending:** 1d100. **61–100** means bending; **1–60** means non-bender.
5. A Nomad bender rolls an element; a non-bender rolls a combat style.

| Nation roll | Origin | Extra origin roll |
|---|---|---|
| 1–25 | Fire Nation | 1d100 for family |
| 26–50 | Water Tribes | 1d3: 1 Southern, 2 Northern, 3 Swamp |
| 51–75 | Earth Kingdom | 1d20: 1–15 village under Fire Nation control, 16–20 no |
| 76–100 | Nomad | None |

Fire Nation families use **1–49 Civilian, 50–79 Military, 80–94 High ranking, 95–100 Royal**. The supplied ranges overlapped at 50, 80, and 95; this resolves those boundaries in favor of the higher tier.

A Fire Nation bender gets Fire bending, a Water Tribes bender gets Water bending, and an Earth Kingdom bender gets Earth bending. **Only a Nomad whose final bending check is above 60** rolls **1d3: 1 Fire, 2 Water, 3 Earth**. A result of exactly 60 is a non-bender and rolls combat style instead. Nomad is an origin, not an Air Nomad. **There is no Air bending.** Every character makes one bending check; there is no second chance check for an element.

Non-benders roll **1d100: 1–20 Sword, 21–40 Bow, 41–60 Fan, 61–80 Fists, 81–100 Pressure point**. The shared endpoint 80 belongs to Fists. Inapplicable dice are never rolled: no tribe outside Water Tribes, no family outside Fire Nation, no village control outside Earth Kingdom, no combat style for benders, and no extra element roll except for Nomad benders.

The message shows the six stat values and each applicable category with its actual roll. It is a character creation result, not a saved or tracked character sheet. Repeat `/avatar` only when your GM permits a new character roll.

## Creator

Open the bot's DMs and send **`!rigger`**. A private panel opens with roll, mode, and outcome menus plus **Choose player**, **Enter value**, **Apply**, and **Turn off** buttons. No arguments are needed. `!Rigger` works too. The live bot opens the panel even if you append old arguments; those arguments do not arm a setting.

Only the account configured as `BOT_OWNER_ID` can open the panel, use its buttons, or submit its forms. It never appears in slash menus. Server messages are ignored. Choose the exact Avatar part when modifying `/avatar`; choosing `/roll` affects custom rolls only. Presets include nations, tribes, family tiers, bender/non-bender, elements, and combat styles. Whole-character Avatar controls support good/bad luck.

The draft defaults to targeting **you**. Use **Choose player** to paste another player's user ID or mention; the bot checks that it is a real player account. The target follows that player across every server and never depends on a server ID or cached server membership. Other players cannot configure Rigger, but the selected player's rolls can receive your setting. Nothing is armed until **Apply**. There is one active setting; applying replaces it. Force, shift, and text-face settings are used once; luck lasts until turned off.

The panel updates its private active status after rolls. Panels close after ten minutes of inactivity or when you reopen them; the saved setting stays active. After a restart, DM `!rigger` for a fresh panel. Older version-3 settings remain active until used, replaced, or turned off; an unrestricted old rule is identified as legacy in the panel. New panel settings always have an explicit player and command scope. See `CREATOR_ONLY.md` for the short guide.

## Railway

For this existing service, retain its attached volume and database path, token, and creator ID. Replace these **four files at the repository root**, then deploy the latest commit:

```text
Dockerfile
requirements.txt
railway.toml
bot.pyz
```

Upload the extracted files, rather than the download ZIP. Keep `bot.pyz` as a file. It already contains the entire minimal runtime, so a flattened GitHub upload cannot cause a missing `ua_bot` folder build error. Railway runs `python bot.pyz`; the Dockerfile validates it during the build. Repository Root Directory should be blank or `/`. Keep one replica and a continuously running service; no public domain or HTTP healthcheck is needed.

For a new service, attach a persistent volume at **`/data`**. Set these variables through your own dashboard:

| Variable | Value |
|---|---|
| `DISCORD_TOKEN` | Your existing Discord bot token |
| `BOT_OWNER_ID` | Your own Discord user ID |
| `BOT_DB_PATH` | Optional: `/data/ua.sqlite3`; omit it to use the actual attached volume automatically |

Railway supplies `RAILWAY_VOLUME_MOUNT_PATH`; do not set it manually. The database must be inside that mount. A local default is `data/ua.sqlite3`. No server ID is needed; a previous `DISCORD_GUILD_ID` is ignored. The bot replaces the global command list and clears old server-specific commands when it connects. Discord clients may need a refresh before their cached menus update.

The bot preserves old campaign tables on the volume without loading them. Current settings and the last 1,000 command receipts use separate tables. Changes and one-use consumption commit together. Redeploys preserve the new setting. A repeated recent interaction returns the same roll or complete Avatar character and does not consume a new setting. All rolls and control changes for one Avatar character commit together.

Install the Discord application **to your server** with `bot` and `applications.commands` scopes; adding it only to your account does not put the bot in the server. Permit View Channel and Send Messages in the roll channel and let players use application commands. Leave the Interactions Endpoint URL empty. No privileged Gateway intents or Administrator permission are needed. Creator controls and notices require that your account can DM the bot. A startup log showing **0 server(s)** means the connected bot was not in any servers when it connected: check its bot ID against the bot in your server and use the correct server install.

## Local editing and checks

Use Python 3.12, extract the full source package, and run:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ua_bot --check
python build_release.py
python bot.pyz --check
```

For local play, copy `.env.example` to `.env`, fill in your token and creator ID, and run `python bot.pyz`. Keep credentials out of source uploads. Rebuild `bot.pyz` after editing source; Railway runs the bundle, not the loose source files. The full ZIP has the proper `ua_bot/` and `tests/` folders for editing. Four-file uploads are for deployment only.

## Troubleshooting

- Bot online but `/roll` or `/avatar` missing: check its server installation, `applications.commands` scope, and channel permissions; refresh Discord's command menu.
- Old commands still visible: refresh Discord. Runtime logs report whether old server commands could be cleared; a reconnect retries failed cleanup.
- Volume error: attach the volume to this service and place the database under its real mount, then redeploy. Retain the original database file when updating.
- Private panel not opening: DM `!rigger` from the exact account identified by `BOT_OWNER_ID`; allow DMs from the bot. This variable must contain your user ID, not the application ID. There is no public `/rigger` command.
- Old or expired buttons: DM `!rigger` again. Reopening does not arm, clear, or rearm a saved setting.
- A setting did not apply: check the panel's **Active setting**, target user ID, and selected roll. Press **Apply** after editing. `/roll` settings never affect `/avatar`; use the Avatar part menu.
- A forced result was impossible or its Avatar part was skipped: the regular roll remains valid and the one-use setting clears. The panel's **Last affected roll** and your private notice explain why.

Official API reference: https://discordpy.readthedocs.io/en/stable/interactions/api.html
