# Private Rigger panel · 3.8.0

**DM the bot `!rigger`.** Only the account configured as `BOT_OWNER_ID` can open and use it. `!Rigger` also works. No extra words or server IDs are needed.

For currency, everyone uses **`/wallet` in the server** to check their own balance. Moderators use **`/wallet-add`**, **`/wallet-remove`**, or **`/wallet-transfer`** with the player(s), amount, wallet, and reason. Money commands require actual server moderation permissions, including for the creator. Use **`/wallet-manage`** to name or create wallets; this is creator-only. Wallet commands and transfers do not roll dice, apply Rigger, or spend rig durations. Full examples are in README.md.

## Add a rig

1. **Choose player** and paste their user ID or mention, or use **Target me**.
2. Choose **/roll**, an **Avatar part**, **Stat 1–6**, **All six stats**, or **Whole character**.
3. Choose Force, Add/subtract, Good luck, Bad luck, Extra dice (highest/lowest), or Text face where available.
4. Pick a preset or enter the value.
5. Press **Duration**. Enter a number such as `3`, or `permanent`, then **Apply**.

Draft edits do not affect rolls until Apply. Targets work across all servers, including players who do not own the bot. To copy an ID: Discord Settings → Advanced → Developer Mode, then right-click the player → Copy User ID. The first draft targets you; reopening resumes the most recently added rig, including its remaining duration, as a draft.

## Duration: uses or permanent

Every kind of rig supports **1–1,000,000 uses** or **permanent**. Press **Duration**, type `3` or `permanent`, and Apply. Each rig has its own counter, including each Stat 1–6 rig. For example, keep Good luck 50% permanent, force Nation to Water for three characters, and force Stat 1 to 18 for just one character.

| Setting | One use means |
|---|---|
| `/roll` | One command, including all dice, bonuses, and highest/lowest selection |
| `/avatar` part or individual stat | One character that uses that rig |
| All six stats / Whole character luck or extra dice | One complete character; all applicable dice receive the change before one use is spent |
| Finite conditional part | One targeted character, even if its branch is skipped; no extra dice are drawn |
| Permanent | Stays until you remove it or change its duration |

Finite rigs expire automatically at zero. **Active rigs** shows `3 uses left`, `1 use left`, or `Permanent`. Counters and permanent rigs survive restarts and Railway redeploys. Other players and other command scopes do not spend uses. Invalid commands and duplicate recent requests do not spend uses. Text luck and fully overridden luck/extra-dice rigs keep their allowances; an impossible force/shift/face attempt spends one use and explains privately. A permanent impossible rig stays active so you can edit or remove it.

Defaults are one use for force/shift/text and permanent for percentage luck or extra dice. Old rigs keep those defaults. **Edit selected** loads the live remaining duration. Applying a reused draft sets that slot's allowance to the displayed count; other rigs keep their counters. Use this to replenish a rig deliberately. Check Duration before applying a reused draft.

## Luck: 1–100% strength

Choose Good luck or Bad luck, then use **Luck %** to type `37` or `37%`. The menu also offers 1/25/50/75/100%. A newly chosen luck mode starts as a **50% draft**.

The percentage controls **how strong the change is**, not its chance of happening. Each numeric die moves that fraction of the distance toward its best/worst legal face. Results round to the nearest legal face, with halfway ties toward the extreme. Very low strength can round to no change.

| Natural d20 | Good luck 50% | Bad luck 50% |
|---|---|---|
| 8 | 14 | 4 |
| 10 | 15 | 5 |
| Any | At 100%: 20 | At 100%: 1 |

Signed dice respect the final total. Bonuses and fixed modifiers stay unchanged. Custom dice use real numeric faces; gaps can make different percentages produce the same result. Highest/lowest selection remains valid. Text dice skip luck. Luck refers to numbers, not whether an origin or combat style is desirable.

Luck follows its chosen Duration. Set `permanent` to keep it until removed, or set a number of uses. **Active rigs → Remove selected** turns it off immediately; 0% is not a setting.

## Secret extra dice

1. DM **`!rigger`**, choose the player, and select **/roll** or the desired Avatar part.
2. Choose **Extra dice · keep highest** or **Extra dice · keep lowest**.
3. Press **Extra dice** and enter **1–100 extra dice per result**, or choose a preset.
4. Choose **Duration**, then **Apply**.

Enter **4** to make `1d20` draw **five d20 candidates** and display only the highest or lowest. The new mode starts as a 4-extra draft. The panel shows `+4 dice (5 total each)` so the count is clear. The player sees an ordinary `1d20` result; extra candidates, their count, and this mode are not included in the public result or receipt.

Each original die gets its own candidates. A `6d20` still displays six numbers, each chosen from five candidates when the extra count is 4. Mixed rolls retain their types: `1d6+1d100` samples d6 and d100 separately. Bonuses and penalties are added once after selection. Public kh1/kl1 works on the selected results. Highest/lowest compares the face values themselves, before any subtraction in the expression.

All supported numbered dice and numeric custom faces work. Weighted lists preserve repeated-face probabilities. **Text/mixed dice use the order you supplied**: first distinct face is lowest, last distinct face is highest. For `["Bronze","Silver","Gold","Bronze"]`, Gold is highest and Bronze is lowest; the repeated Bronze increases its probability without changing its rank. Numeric lists always use numeric order, even when listed out of order.

This mode samples real dice, so five d20 candidates can still all be low. Use Force when you need an exact total. Extra-highest and extra-lowest share one slot per player/roll, while percentage luck has its own separate slot. One command spends one use regardless of the extra count; whole-character and all-stat settings spend one use per complete character. Defaults are permanent unless Duration is changed.

**Active rigs** shows direction, extra count, total candidates per result, and remaining duration. Edit selected changes it; Remove selected turns it off. Targets work across servers without a server ID.

## Multiple rigs on one Avatar

Apply adds a rig or updates only the **same player + roll + kind**. Other rigs stay active. Good and bad share one percentage-luck slot; extra-highest and extra-lowest share a separate extra-dice slot.

Example: for one player, force Nation to Water Tribes, force Bending check to Bender, and set Stat 1 to 18, Stat 2 to 14, and the other stats individually. All those rigs affect the same next `/avatar`.

**Stat 1–6** changes the first through sixth displayed d20s. Each supports force (1–20), shift, percentage luck, or extra dice. Only extra-dice mode draws more candidates for that slot. **All six stats** and **Whole character** support percentage luck and extra dice.

When settings overlap:

- A stat's own setting overrides all-six-stats, then whole-character settings of the same kind. Other specific parts override whole-character settings of that kind.
- Each part applies **extra dice → percentage luck → shift → exact force**. Force wins. Extra candidates are drawn before other changes; only the final result is public.
- Every rig follows its own duration. Reapplying a slot updates its value and resets its allowance to the displayed duration without adding duplicates.

Up to **100 rigs total** can be saved across all players. `/roll` rigs stay separate from Avatar rigs.

## Check, edit, and remove

Press **Active rigs** to see every rig's number, player ID, roll, value/percentage, and duration. **Only chosen player** filters to the ID displayed above the list. Use Previous/Next for longer lists.

- Select an entry, then **Edit selected** to load its draft. Apply saves it. Changing its player, roll, or kind creates another slot and leaves the original active.
- **Remove selected** clears only that entry.
- **Clear player** clears rigs for the **Chosen player ID shown above the list**.
- **Clear all** removes every rig.
- **Refresh** checks live state. **Back to draft** retains your unsaved edits.

The compact main panel shows just Player, Roll, Change, and Duration, with live active counts in its footer. Unneeded preset menus are hidden. **Active rigs** holds the full list, **Last affected roll**, Refresh, and Clear all. Status updates privately after rolls. A draft can still show a value or duration after a rig expires; Active rigs is the live list.

## Avatar choices

| Part | Forced range | Presets |
|---|---|---|
| IQ / Stat 1–6 | 1–20 | Enter value |
| Nation | 1–100 | Fire, Water, Earth, Nomad |
| Water tribe | 1–3 | Southern, Northern, Swamp |
| Fire family | 1–100 | Civilian, Military, High ranking, Royal |
| Earth village | 1–20 | Under Fire Nation control / not under control |
| Bending check | 1–100 | Bender (61), Non-bender (60) |
| Nomad element | 1–3 | Fire, Water, Earth |
| Non-bender combat | 1–100 | Sword, Bow, Fan, Fists, Pressure point |

Final rigged values determine later rolls. **Only a final Nomad with bending above 60 rolls the element d3.** Other benders receive their nation's element. At 60 or below, the character rolls non-bender combat. There is no Air bending. Water's tribe d3 is a separate origin roll.

A skipped conditional part draws no extra dice. Its finite rig spends one character use; its permanent rig stays active. Impossible force/shift requests spend one use of that rig, leave that change unapplied, and explain privately; permanent rigs stay. Other successful changes remain effective. Custom `/roll` force includes modifiers and bonuses in its exact total.

## Simple custom rolls

Players now enter everything in one **dice** field: `1d100`, `1d100+2`, or `1d100-2`. The result shows the rolled die, the declared Bonus/Penalty, and the final total. Force means the **final total**, so forcing 50 on `1d100+2` shows a die of 48, Bonus +2, Total 50; on `1d100-2` it shows a die of 52, Penalty -2, Total 50. A requested total must still be possible on that die.

Good/bad luck and shifts preserve the typed modifier. Weighted faces work inline, such as `2d[0,1,1,5]+2`; text faces use `1d["Sun","Rain"]`. Text face rigs match the exact capitalization. Highest/lowest uses `3d20kh1+2` or `3d20kl1-2`. All modes keep their existing owner-only controls, player targets, and durations.

## Restarts and privacy

Saved rigs survive Railway redeploys. Dice, rig consumption, and the complete character receipt commit together. Duplicate recent requests do not reroll, consume newer rigs, or rearm used ones. Public results show only final dice and outcomes.

Panels close after ten minutes of inactivity, when reopened, or after a restart. This keeps saved rigs active. DM `!rigger` for a fresh panel. Old buttons and forms cannot change settings.

Old settings migrate with their target and last status intact. Old luck without a percentage becomes **100% strength**; adjust it if needed. Legacy unrestricted or six-stat-total rigs remain visible and removable. Create new explicit /roll or Avatar rigs instead of editing legacy entries. Legacy total rigs run before new individual stat overrides. Keep this guide private; source-code readers can inspect the feature.
