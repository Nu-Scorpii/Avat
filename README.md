# Simple Discord Dice Bot · 3.6.0

Players use `/roll`, `/avatar`, and `/wallet`. Moderators use separate currency commands to add, remove, or transfer money. Creator roll controls work privately in DMs.

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

## Wallets: simple commands

**Everyone can use `/wallet`.** It opens your own private balance card with a wallet dropdown, History, and Refresh. There are no money-editing buttons in this player command, even for moderators or the creator. Existing wallets stay available. A server without a wallet automatically gets **Main / coins**, with every player starting at zero; no creator setup is required to check your balance.

| Command | Who can use it | What it does |
|---|---|---|
| `/wallet [wallet]` | Every player | Your balance, recent activity, and paged history |
| `/wallet-add player amount [wallet] [reason]` | Server moderators | Add money to a selected player |
| `/wallet-remove player amount [wallet] [reason]` | Server moderators | Remove money without allowing an overdraft |
| `/wallet-transfer sender receiver amount [wallet] [reason]` | Server moderators | Move money between two players for a session deal |
| `/wallet-manage` | Bot creator | Create wallets or edit names and currency labels |

Examples show the values to choose in Discord's slash options:

```text
/wallet
/wallet-add player:@Alex amount:100 reason:Quest reward
/wallet-remove player:@Alex amount:25 reason:Shop purchase
/wallet-transfer sender:@Alex receiver:@Sam amount:75 reason:Sword purchase
/wallet-transfer sender:@Alex receiver:@Sam amount:75 wallet:Avatar reason:Sword purchase
/wallet-manage
```

Select real members with Discord's player picker; select wallet names from the autocomplete suggestions, or type an exact wallet name. If there is one wallet, money commands can omit it. **If there are several wallets, money commands require you to choose one** to avoid changing the wrong campaign's money. `/wallet` can omit it and lets you switch with the dropdown.

**Only actual server moderators can add, remove, or transfer money.** Accepted permissions are Administrator, Manage Server, Manage Messages, Timeout Members (Moderate Members), Kick Members, or Ban Members. Permission checks run in the bot for every command, including after member checks. Being the bot creator or having a role named Mod does not bypass them. `/wallet` has no moderator permission restriction; server admins can still control application-command access through Discord's own server settings.

**Transfers pay the receiver from the sender's balance.** They do not create money. Both players must be different current human members of the same server, using the same named currency wallet. An unaffordable payment or a receiver exceeding the balance limit changes neither account. Debit, credit, both history entries, and the duplicate-request receipt save together. Two simultaneous payments cannot spend the same money twice.

Every change records the moderator, amount, reason, date, and resulting balance. Transfers also appear in both players' histories with the other player's ID and the same deal number. Moderator confirmations are private, and players see their updated balance with `/wallet` or Refresh. Reasons default to Session reward, Session expense, or Session deal if omitted.

The creator uses **`/wallet-manage`**, then New wallet or Edit wallet to name up to **25 wallets per server** and their currency labels. The automatic Main wallet can be renamed. Renaming keeps all balances and history; changing a label does not convert money. Wallets and balances remain separate for each server, wallet, and player.

Panels close after ten minutes of inactivity or a restart; use `/wallet` again. All saved wallets, balances, old history, and durable currency receipts survive redeploys. Existing version-3.5 data migrates without resetting anything. Wallet commands do not draw dice, apply Rigger, or spend rig uses. Whole currency units and the existing **1 trillion** per-player balance limit remain.

## Creator

Open the bot's DMs and send **`!rigger`**. Choose a player, roll, and change, enter a value or pick a preset, choose **Duration**, then press **Apply**. Enter a number such as `3`, or `permanent`. `!Rigger` works too. No command arguments or server IDs are needed. Appended old arguments open the panel without arming anything.

Only the account configured as `BOT_OWNER_ID` can open the panel, use its buttons, or submit its forms. It never appears in slash menus. Server messages are ignored. Choose the exact Avatar part when modifying `/avatar`; choosing `/roll` affects custom rolls only. Presets include nations, tribes, family tiers, bender/non-bender, elements, and combat styles. Whole-character Avatar controls support good/bad luck.

The first draft targets **you**; reopening resumes the most recently added rig as a draft. **Choose player** accepts another player's user ID or mention and verifies their account. Targets follow players across every server. Other players cannot operate the controls but can receive rigs you set for them. Only **Apply** changes live settings.

**Good/bad luck has 1–100% strength.** Use **Luck %** to enter `37` or `37%`, or pick 1/25/50/75/100 from the menu. Each numeric die moves that fraction toward its best/worst legal face, rounded to the nearest legal value; ties round toward the extreme. **50% means halfway; 100% gives the best/worst face.** Strength is not a chance of activation. Tiny strengths can round to no change. Signed dice respect the final total; bonuses stay unchanged; text dice skip luck.

**Several rigs can affect one Avatar character.** Apply adds or updates only the same player + roll + kind of change. For example, force Nation to Water Tribes, force Bending to 100, and set each **Stat 1–6** independently to 1–20. Force, shift, and luck can coexist on one part. Good and bad share one luck slot. Specific luck overrides whole-character luck; a stat's luck overrides all-six-stats luck. Each part applies luck, then shift, then exact force. Force wins.

**Every rig has its own duration.** Use **Duration** to set 1–1,000,000 uses, or `permanent` until removed. One `/roll` command spends one use, even for a pool of dice. One `/avatar` character spends one use of each affected rig: whole-character and all-six-stats luck affect every applicable die before their counters decrease once. Each Stat 1–6 rig can have a different duration. Finite conditional-part rigs reserve character uses, so a skipped part also spends one use of that rig without drawing extra dice. Permanent rigs remain active. Other players, other command scopes, invalid input, recent duplicate requests, skipped text luck, and fully overridden luck do not spend uses. Impossible changes spend one use and explain privately.

Without a chosen duration, force/shift/text defaults to one use and luck to permanent. Existing rigs retain those defaults. Reopening or editing a rig loads its current remaining uses into the draft. **Apply sets only that slot's allowance to the duration shown**, so reapplying can replenish it; duplicate deliveries of the same Apply cannot. Check the Duration field before applying a reused draft.

**Stat 1–6** means the first through sixth values displayed in the existing 6d20 roll. It does not roll extra dice. **All six stats** and **Whole character** support luck; choose individual stats for exact values or point shifts.

Press **Active rigs** to see every active rig with its player, roll, value/percentage, and duration. Use **Only chosen player**, page buttons, **Edit selected**, **Remove selected**, **Clear player**, or **Clear all**. The draft also shows active counts and a quick preview for the chosen player. Private status refreshes after rolls. Up to 100 independent rigs can be saved.

Panels close after ten minutes of inactivity or when reopened; saved rigs stay active. After a restart, DM `!rigger` for a fresh panel. Old version-3 settings migrate with their target and last status intact; old luck without a percentage becomes **100% strength**. Legacy unrestricted or six-stat-total rules remain visible and usable once; remove them to create explicit command/part controls. See `CREATOR_ONLY.md` for the guide.

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

The bot preserves old campaign tables on the volume without loading them. Current rigs and the last 1,000 dice receipts use separate tables. All dice, rig consumption, and a receipt for one Avatar character commit together. Wallet balances, history, and durable currency receipts use their own tables. Redeploys preserve rigs and wallets. A repeated recent dice interaction returns the same result without consuming or rearming newer rigs; duplicate currency submissions are remembered independently of the dice cache.

Install the Discord application **to your server** with `bot` and `applications.commands` scopes; adding it only to your account does not put the bot in the server. Permit View Channel, Send Messages, and Embed Links for the wallet cards, and let players use application commands. Leave the Interactions Endpoint URL empty. No privileged Gateway intents or Administrator permission are needed. Creator controls and notices require that your account can DM the bot. A startup log showing **0 server(s)** means the connected bot was not in any servers when it connected: check its bot ID against the bot in your server and use the correct server install.

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

- Bot online but `/roll`, `/avatar`, or `/wallet` missing: check its server installation, `applications.commands` scope, and channel permissions; refresh Discord's command menu.
- Checking a new server: `/wallet` creates an empty Main wallet automatically. The creator can rename it or create more with `/wallet-manage`.
- Adding or moving money: use `/wallet-add`, `/wallet-remove`, or `/wallet-transfer` with actual server moderation permissions. The player balance panel only shows your money and history. Choose a wallet if several exist.
- Old commands still visible: refresh Discord. Runtime logs report whether old server commands could be cleared; a reconnect retries failed cleanup.
- Volume error: attach the volume to this service and place the database under its real mount, then redeploy. Retain the original database file when updating.
- Private panel not opening: DM `!rigger` from the exact account identified by `BOT_OWNER_ID`; allow DMs from the bot. This variable must contain your user ID, not the application ID. There is no public `/rigger` command.
- Old or expired buttons: DM `!rigger` again. Reopening does not arm, clear, or rearm a saved setting.
- A rig did not apply: open **Active rigs**, check its player ID, roll, value/strength, and remaining uses. Press **Apply** after draft edits. Specific luck overrides broader luck; exact force wins over luck or a shift. Small percentages may round to no change. `/roll` rigs do not affect `/avatar`.
- A forced result was impossible or its Avatar part was skipped: the regular roll remains valid; finite rigs spend one use and expire at zero, while permanent rigs stay. The panel's **Last affected roll** and your private notice explain why.

Official API reference: https://discordpy.readthedocs.io/en/stable/interactions/api.html
