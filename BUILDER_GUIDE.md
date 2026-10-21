# Your server's command workshop · 4.1.1

Start with `/builder`. The workshop opens a private editor for the staff member who ran it. Select **New command**, choose a type, and give it a slash-command name. Forms save a draft; **Publish** makes that draft available to players.

## Character creation commands

Choose **Character rolls** and add separate groups such as Origin `1d5`, Stats `6d20`, and Power `1d20+2`. Each group keeps its own label. Normal expressions support arbitrary numbered dice, mixed pools, modifiers, keep-high/low, and JSON custom faces. Use six named `1d20` groups when every stat needs its own label; use one `6d20` group when the values belong together.

## Named probabilities

Choose **Add outcome → Named probabilities** and enter one result per line:

```text
Civilian family | 50%
Military family | 30%
High ranking family | 15%
Royal family | 5%
```

The chances must total exactly 100%. Positive decimal chances with up to four decimal places are supported. Players see only the chosen name, without a numeric die or total. You can combine several probability types with normal dice groups in one character command.

Choose **Relative weights** when ratios are easier. `Rare | 1` and `Common | 3` produce 25% and 75%. Relative weights do not need to total 100 and include a numeric draw in the result.

## Conditional rolls

Select an entry and press **Condition**. A condition may reference an earlier result:

| Condition | Meaning |
|---|---|
| `Bending >= 61` | Roll only when the earlier total is at least 61 |
| `Nation == Water` | Roll only when the earlier named result is Water |
| `Bending == Bender` | Roll only when the named result is Bender |
| `Power < 10` | Roll only below a total of 10 |

Numeric results support `==`, `!=`, `>`, `<`, `>=`, and `<=`. Named or text results support `==` and `!=`. A skipped source also skips its dependent rolls. Conditions keep stable references when an entry is renamed; invalid removal or reordering is rejected.

## Publishing and maintenance

- **Name & style** changes the title, introduction, and accent colour.
- **Move up / Move down** changes the display order while preserving valid dependencies.
- **Preview** creates a private sample only.
- **Publish** updates the live command and its server slash entry.
- **Unpublish** removes player access while retaining the draft.
- **Archive / Restore** hides an old definition and restores it later without publishing it.

Players can run the published slash command directly or find it through `/custom`. If Discord's server-menu sync fails, the saved command remains available through `/custom` while staff retry Publish or reconnect the bot.

## FAQ and shop commands

An **FAQ / guide** contains named questions and answers. Players select a question from a private dropdown.

A **Shop** contains item names, descriptions, and whole-number prices. Select the server wallet used for purchases. Players review the item, quantity, and current price before confirming. Successful purchases atomically update the buyer's balance, ledger, and saved inventory.

## Permissions and limits

| Action | Required access |
|---|---|
| Build character commands | Server owner, Administrator, or Manage Server |
| Build FAQs and shops | The above or an accepted moderation permission |
| Run published commands and browse shops | Every server player, subject to Discord permissions |
| Add, remove, or transfer money | Accepted server moderation permission |
| Create or rename wallets | Bot creator |

Limits are 20 command slots per server, 20 entries per command, 200 base dice per character command, and 25 outcomes per named type. Drafts, publications, inventories, balances, and transaction history persist on the existing Railway volume.
