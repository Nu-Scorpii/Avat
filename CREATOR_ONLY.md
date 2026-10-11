# Private Rigger panel · 3.2.0

**DM the bot `!rigger`.** This opens the panel. No extra words, numbers, server IDs, or slash commands are needed. `!Rigger` also works. Only the account configured as `BOT_OWNER_ID` can open or operate it. DMs keep it out of player channels; privileged Message Content intent is not required.

## Use it in four steps

1. **Choose the roll:** custom `/roll`, one `/avatar` part, or whole-character Avatar luck.
2. **Choose the change:** Force a result, Add/subtract points, Good luck, Bad luck, or Text face.
3. **Choose the player:** it starts with you. To affect someone else, press **Choose player** and paste their user ID or mention. The bot verifies that it is a player account. **Target me** returns to you.
4. **Pick an outcome or Enter value**, then press **Apply**.

**Editing is a draft. Apply arms it.** The panel shows the draft and the separate **Active setting** so you can tell what will affect the next roll. **Turn off** clears the live setting immediately; **Refresh** checks its current status; **Help** explains the buttons.

There is **one active setting**. Each Apply replaces it. Targets follow a player in every server the bot joins. Another player's rolls do not consume that player's setting. Only you operate the panel; your selected target does not need to own the bot.

To copy a player ID, enable **Discord Settings → Advanced → Developer Mode**, then right-click their profile → **Copy User ID**. Use their user ID, not a server ID, channel ID, or application ID.

## Choose the change

| Change | What to enter | How long it lasts |
|---|---|---|
| Force a result | Exact final total, or a preset outcome | One matching roll |
| Add/subtract points | Whole number, such as `+3` or `-2` | One matching roll |
| Good luck | Nothing | Until Turn off or replaced |
| Bad luck | Nothing | Until Turn off or replaced |
| Text face | Exact custom die label, preserving capitals and spaces | One matching custom `/roll` |

Force includes arithmetic and bonuses: a forced total of 15 on `1d20` with `bonus:3` shows a die of 12 and total 15. Multi-die force changes legal die faces to reach the total; it does not give every die that number. Good/bad rolls the entire selected pool twice and keeps the higher/lower total, including subtraction and highest/lowest selection. Luck refers to the numeric value, not a judgment about which nation is best.

If a force or shift cannot be produced by the real die faces, the result stays normal and the one-use setting clears. Only you receive the explanation. Text dice have no numeric total; use **Text face** for one custom die instead. Luck skips text dice and remains on.

## Avatar choices

**Choose the Avatar part in the first menu.** Custom `/roll` settings do not affect `/avatar`, and Avatar settings do not affect `/roll`. Force or shift applies to exactly the part you choose, instead of silently changing IQ. **Whole character** supports good/bad luck on every applicable part.

| Avatar part | Exact forced range | Preset choices |
|---|---|---|
| IQ | 1–20 | Enter value |
| Six stats | Total 6–120 | Enter value; 120 gives six 20s |
| Nation | 1–100 | Fire Nation, Water Tribes, Earth Kingdom, Nomad |
| Water tribe | 1–3 | Southern, Northern, Swamp |
| Fire family | 1–100 | Civilian, Military, High ranking, Royal |
| Earth village | 1–20 | Under Fire Nation control, Not under control |
| Bending check | 1–100 | Bender (61), Non-bender (60) |
| Nomad element | 1–3 | Fire, Water, Earth |
| Non-bender combat | 1–100 | Sword, Bow, Fan, Fists, Pressure point |

Presets force a valid representative die value. You can use **Enter value** instead when you want an exact number. The resulting number determines subsequent branches. For example, choosing Water Tribes produces the tribe d3; choosing a bending result of 60 produces non-bender combat.

The **element d3 runs only when the final nation is Nomad and the final bending check is above 60**. A non-Nomad bender receives their nation's element automatically. A Nomad at 60 or below receives combat style instead. No extra bending check or Air bending is added. Water characters still roll their separate origin tribe d3 regardless of bending.

If a one-use conditional part is absent from the selected player's character, that setting clears after the character and explains the skipped part privately. It cannot invent an extra tribe, family, village, element, or combat roll. A lasting luck setting stays enabled when its part is skipped.

## Status and restarts

The panel refreshes after rolls and shows the **Last affected roll** privately. Force/shift/text-face settings clear after one use. Saved settings survive Railway redeploys, and repeated deliveries do not rearm or consume them twice.

Panels close after ten minutes of inactivity, when reopened, or when the bot restarts. **A closed panel does not turn off a saved setting.** DM `!rigger` to open a fresh panel. Old buttons and old forms cannot change settings after the panel closes. Settings from older version-3 releases are preserved; the panel labels unrestricted old rules as legacy. New settings always have an explicit player and command scope.

Public results contain only the dice and outcome. The panel is absent from slash menus. Keep this guide private; source-code readers can still inspect how the bot works.
