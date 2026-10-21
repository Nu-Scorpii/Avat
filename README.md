# Simple Discord Dice Bot · 4.1.1

This bot provides custom dice, Avatar character creation, server currencies, and a workshop for server-specific character rolls, FAQs, and shops. Its public Discord interface contains nine global slash commands plus any custom commands published by a server.

## Commands

| Command | Who can use it | Purpose |
|---|---|---|
| `/roll [dice]` | Everyone | Roll any supported dice expression |
| `/avatar` | Everyone | Generate an Avatar character |
| `/wallet [wallet]` | Everyone | View your balance, history, and items |
| `/wallet-add` | Server moderators | Add currency to a player |
| `/wallet-remove` | Server moderators | Remove currency from a player |
| `/wallet-transfer` | Server moderators | Transfer currency between players |
| `/wallet-manage` | Bot creator | Create or rename server wallets |
| `/builder` | Server staff | Build character rolls, FAQs, and shops |
| `/custom [command]` | Everyone | Browse or run published server commands |

## Dice rolls

`/roll` has one optional field. Leave it blank for `1d20`, or enter expressions such as:

| Expression | Result |
|---|---|
| `1d100` | One 100-sided die |
| `1d100+2` | Roll, then add 2 |
| `1d100-2` | Roll, then subtract 2 |
| `6d20+3` | Six d20s plus 3 once |
| `2d17+1d8-3` | Mixed dice sizes and a penalty |
| `3d20kh1+2` | Keep the highest d20, then add 2 |
| `3d20kl1-2` | Keep the lowest d20, then subtract 2 |
| `1d["sun","rain","rain","storm"]` | Weighted text faces |

The result shows every public die, a Bonus or Penalty line when present, and the final total. Limits are 100 dice, 20 terms, 1–1 billion sides, and 500 characters per expression. Text faces use JSON strings and cannot use arithmetic.

## Avatar character creation

`/avatar` rolls IQ (`1d20`), six stats (`6d20`), nation (`1d100`), the applicable origin detail, and bending (`1d100`). Results of 61–100 receive bending and a separate Bending Strength `1d20`; results of 1–60 receive a non-bender combat style.

| Nation roll | Origin | Extra roll |
|---|---|---|
| 1–25 | Fire Nation | Family: 1–49 Civilian, 50–79 Military, 80–94 High ranking, 95–100 Royal |
| 26–50 | Water Tribes | `1d3`: Southern, Northern, or Swamp |
| 51–75 | Earth Kingdom | `1d20`: 1–15 under Fire Nation control, 16–20 not controlled |
| 76–100 | Nomad | No origin-detail die |

Fire Nation, Water Tribes, and Earth Kingdom benders receive their matching element. A Nomad bender rolls `1d3` for Fire, Water, or Earth. There is no Air bending. Non-benders roll `1d100`: Sword 1–20, Bow 21–40, Fan 41–60, Fists 61–80, or Pressure point 81–100.

## Server workshop

Run `/builder`, select **New command**, and choose:

- **Character rolls** for multiple named dice groups, named probability results, relative weights, and conditional follow-up rolls.
- **FAQ / guide** for browsable questions and answers.
- **Shop** for wallet-backed purchases and saved player inventories.

A character command can combine `1d5`, `6d20`, a separate `1d20+2`, and any number of named outcome types in one result. **Named probabilities** use exact chances totaling 100% and display only the selected name. **Relative weights** use ratios and display the selected name with a numeric draw.

Changes remain drafts until **Publish**. **Preview** produces a private sample without saving a character result or purchasing anything. Each server owns its definitions, and published commands are restored when the bot reconnects. See [BUILDER_GUIDE.md](BUILDER_GUIDE.md) for the complete workflow.

## Wallets and shops

Every server receives a default **Main / coins** wallet when needed. Players use `/wallet`; only members with real moderation permissions can add, remove, or transfer currency. Transfers debit one player and credit the other in one transaction. Wallets, balances, histories, shop inventories, and duplicate-request receipts persist on the Railway volume.

Shops use one server wallet, have unlimited stock, and require the buyer to review and confirm the quantity and current price. Purchases update the balance, ledger, and inventory together.

## Railway

The runtime needs `Dockerfile`, `requirements.txt`, `railway.toml`, and `bot.pyz` at the repository root. Set `DISCORD_TOKEN` and `BOT_OWNER_ID`. Attach one persistent volume at `/data`; the bot automatically stores its SQLite database there. `BOT_DB_PATH=/data/ua.sqlite3` is optional.

Keep one continuously running replica. No public domain, HTTP healthcheck, server ID, Administrator permission, or privileged Gateway intent is needed. Railway starts the bot with `python bot.pyz`, and the bundle validates all nine global commands during the image build.

## Local validation

Use Python 3.12:

```text
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ua_bot --check
python build_release.py
python bot.pyz --check
```

Never commit a real Discord token. The included `.env.example` contains placeholders only.

## Troubleshooting

- Missing slash commands: refresh Discord, confirm the application was installed to the server with `bot` and `applications.commands`, and allow application commands in the channel.
- Bot offline: check the latest Railway deployment and its startup logs.
- Volume error: attach the persistent volume at `/data`, then redeploy.
- Wallet command rejected: select a wallet when the server has several and confirm the acting member has an accepted moderation permission.
- Published custom command missing: use `/custom` immediately, then republish or reconnect to retry the server slash-menu sync.
