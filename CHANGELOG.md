# Version 3.9.0

- Added a separate Bending Strength 1d20 to every Avatar bender, including all three Nomad elements. Non-benders neither roll nor display it; IQ and the original six stats keep their own dice.
- Use the final controlled bending check to choose the branch. The existing threshold remains 61–100 for bending, with the element d3 still limited to Nomad benders.
- Added /avatar · Bending Strength to the private !rigger panel. Support exact 1–20 values, shifts, percentage good/bad luck, extra-dice highest/lowest, stacking, player targets, active status, and counted/permanent durations.
- Include strength in whole-character luck/extra dice, with specific-strength overrides. Keep all-six-stats controls separate and follow existing finite skipped-part duration behavior. Preserve old receipt replays without generating missing strength rolls.
- Verified 618 tests, including 36 new conditional-strength, Rigger, persistence, privacy, and UI checks. Source, bundle, and isolated four-file startup checks validate all seven commands.

# Version 3.8.0

- Added Extra dice · keep highest and Extra dice · keep lowest to the private !rigger panel. Choose 1–100 extra candidates per original die; 4 extra makes a normal 1d20 sample five d20s and display one winner.
- Sample the same die size or custom weighted faces independently for every original die. Numeric faces use numeric order; text/mixed faces use first-occurrence list order. Preserve normal public dice counts, expressions, bonuses, penalties, and kh1/kl1; never include discarded candidates in the public result.
- Support /roll, individual Avatar parts and stats, all six stats, and whole characters. Select final winners before Avatar branching; avoid sampling all-stat extras twice.
- Keep highest/lowest in a shared extra-dice slot separate from percentage luck. Apply extra dice before luck, shifts, and exact force, with specific-part overrides. Preserve owner-only DM controls, player targeting, counted/permanent durations, receipts, old rigs, wallets, and transfers.
- Added a count form, quick presets, clear extra/total labels, live active status, and editing. New extra-dice drafts use 4 extra and default to permanent until Duration is changed.
- Verified 582 tests, including 58 new candidate-selection, privacy, custom-face, Avatar, duration, persistence, replay, rollback, authorization, and UI regressions. Source, bundle, and isolated four-file startup checks validate all seven commands.

# Version 3.7.0

- Simplified /roll to one optional dice field: 1d100, 1d100+2, or 1d100-2; the default remains 1d20. Removed separate bonus, faces, and keep fields.
- Show each rolled value, a clear Bonus or Penalty line when supplied, and the final total. Multiple modifiers show their terms and net change; points are applied once.
- Preserved custom weighted/text faces and highest/lowest through the same field, using 2d[0,1,1,5]+2, 1d["Sun","Rain"], 3d20kh1+2, or 3d20kl1-2.
- Decluttered the private Rigger editor to Player, Roll, Change, and Duration with live counts. Hide unused preset menus; move detailed status, Refresh, and clearing actions into Active rigs.
- Kept final-total forcing, shifts, percentage luck, text faces, owner-only DM controls, cross-server targeting, independent stacked Avatar rigs, individual stats, durations, and saved wallets intact.
- Verified 524 tests, including 37 new single-field, modifier, rig compatibility, custom-face, replay, and compact UI regressions. Source, bundle, and isolated four-file startup checks validate all seven commands.

# Version 3.6.0

- Rebuilt /wallet as an unrestricted player balance/history command with a simple dropdown, History, and Refresh. New servers get an empty Main wallet automatically.
- Moved all money changes into moderator-only /wallet-add, /wallet-remove, and /wallet-transfer commands with actual member pickers, wallet autocomplete, optional reasons, and private confirmations. The creator does not bypass moderator checks.
- Added atomic same-wallet player transfers, conserved balances, linked deal histories, durable duplicate protection, current-member validation, overdraft/limit checks, and rollback of both sides on failure.
- Added creator-only /wallet-manage for wallet naming and creation. Multi-wallet money commands require an explicit wallet choice.
- Preserved v3.5 balances, old history, existing receipts, and all Avatar/Rigger behavior. Failed confirmation delivery never invites an automatic second payment.
- Verified 487 tests, including 38 transfer/command tests, two simultaneous database writers, migration, permissions, UI payloads, and existing game regressions.

# Version 3.5.0

- Added /wallet with private teal balance cards, named-wallet selection, member selection for moderators, add/remove forms, recent activity, paged history, My balance, and Refresh.
- Added creator-only creation and editing of up to 25 named wallets per server, with custom currency labels. Each player's balances remain separate per server and wallet; renaming preserves amounts and history.
- Required real server moderator permissions for every money change, including changes by the bot creator. Rechecked viewer, server, current member, permissions, selected target, and form expiry; ordinary players view only their own balances.
- Recorded reasons, amounts, moderator IDs, timestamps, and resulting balances. Prevented overdrafts, invalid whole amounts, duplicate awards/removals, and partial database writes.
- Kept currency tables and durable receipt records separate from dice and Rigger. Existing Avatar mechanics, secret controls, percentages, and rig durations remain unchanged.
- Verified 452 tests, including 62 new currency, UI, isolation, permission, replay, persistence, rollback, and regression tests. The deployment bundle validates /roll, /avatar, and /wallet.

# Version 3.4.0

- Added Duration to the creator-only DM panel: every rig supports a chosen number of uses or permanent until removed, including force, shift, numeric luck, and text faces.
- Tracked remaining uses independently for every player/part/kind, including all six individual stat rigs. Active rigs and the draft show duration; Edit selected loads the live remaining allowance.
- Counted one `/roll` pool or one complete `/avatar` as one use per affected rig. Whole-character and all-stat luck finish all applicable dice before decrementing once. Finite conditional rigs reserve character uses, including skipped branches; permanent rigs remain.
- Preserved counters across restarts, duplicate-request protection, owner-only controls, global user targets, legal dice, and atomic character/rig/receipt writes. Existing force/shift/face rigs migrate to one use; luck remains permanent.
- Verified 390 tests, including 55 duration tests covering every mode, per-stat counters, mixed durations, persistence, replays, rollback, skip/failure behavior, owner/stale-form checks, and real UI payloads.

# Version 3.3.0

- Added 1–100% good/bad luck strength and input accepting `50` or `50%`. Numeric faces move that fraction toward their legal best/worst face; signed dice and keep-high/low remain valid; text dice skip luck.
- Replaced the single setting with up to 100 independent rig slots. Apply updates only the same player, command/part, and kind; multiple rigs can affect one complete Avatar.
- Added Stat 1–6 targets to independently force, shift, or apply luck to each ordered 6d20 outcome, without drawing extra dice. All-six-stats and whole-character choices support luck.
- Defined precedence: specific luck overrides broader luck; luck runs before point shifts and exact force. Force wins. Good and bad share one luck slot.
- Added Active rigs with counts, player IDs, values, percentages, durations, pages, player filtering, editing, individual removal, player clearing, and clearing all rigs. Status refreshes privately after rolls.
- Preserved owner-only DM authorization, cross-server targets, strict Nomad bending branching, old settings/receipts, and atomic complete-character consumption. Failed/skipped rigs clear individually. Old luck becomes 100% strength until edited.
- Verified 335 tests, including 62 new percentage, stacking, per-stat, migration, rollback, management, and Discord payload tests.

# Version 3.2.0

- Replaced the live Rigger argument interface with a creator-only DM panel opened by `!rigger` or `!Rigger`.
- Added explicit player targeting, per-command and Avatar-part menus, preset outcomes, editable values, Apply, Turn off, Refresh, and Help. Draft changes never arm a setting.
- Defaulted new controls to the owner, verified copied player IDs through Discord, and allowed selected non-owner players to receive controls across servers without server IDs or cached membership.
- Checked creator authorization at panel, button, select, modal, and engine boundaries. Reopening invalidates old controls; expired forms cannot apply changes.
- Separated `/roll` settings from Avatar settings. Added whole-character Avatar luck while keeping force/shift tied to a specific Avatar part.
- Corrected bending to strictly above 60: 1–60 is non-bender; 61–100 is bender. Only a Nomad bender draws the element d3, using the final controlled bending outcome.
- Refreshed private active status after rolls. Kept persistent storage, atomic one-use consumption, duplicate-request handling, and the two-command public interface.
- Added panel, owner authorization, non-owner targeting, scope, timeout, persistence, payload, and strict bending regression coverage. All 273 tests pass.

# Version 3.1.0

- Added `/avatar`: IQ 1d20, six stat d20s, nation, conditional origin, bending check, and a Nomad element or non-bender combat style.
- Implemented the supplied ranges with deterministic boundaries: Fire families 1–49 / 50–79 / 80–94 / 95–100; Pressure point 81–100. Bending starts at 60.
- Added simple creator part controls, such as `!Rigger nation 30` and `!Rigger bending 100`, with the usual force, shift, luck, and cross-server user targeting.
- Shared the stable roll-control code with `/roll`; Avatar-only settings never affect ordinary custom rolls.
- Used modified outcomes for later decisions; skipped branches draw no dice. No Air bending is generated.
- Kept one active setting. A skipped one-use part clears privately after the targeted character; lasting luck remains active.
- Stored a whole character result, setting changes, and replay receipt in one transaction. Duplicate interactions return the same complete character.
- Preserved existing version-3 settings and the Railway volume. Added 92 regression tests; all 231 automated tests pass.

# Version 3.0.0

- Replaced the full game bot with one public command: `/roll`.
- Removed all character, combat, attendance, progression, FAQ, saved-die management, panels, and game-rule features from the runtime.
- Retained arbitrary numbered dice, mixed signed expressions, per-roll weighted or text faces, separate bonuses, and keep-high/low.
- Rebuilt Rigger around one active creator-only DM setting. Force/shift are one-use; good/bad is lasting. Each new setting replaces the previous one.
- Added simple shorthand, an optional user target across every server, and exact text-face forcing.
- Enforced legal faces and exact final totals. Impossible requests and bounded-search failures leave the roll normal, clear the one-use setting, and notify only the creator.
- Validated all input before drawing dice or consuming a setting. Made text-containing dice consistently nonnumeric.
- Committed settings and recent roll receipts atomically; repeated interactions do not consume controls twice. Kept old volume tables untouched and inactive.
- Removed stale global and server-specific game commands during startup. Removed the need for a server ID.
- Reduced runtime dependencies to discord.py and python-dotenv. Kept the four-file Railway Docker deployment and persistent-volume checks.
- Verified 139 focused automated tests, real Discord command serialization, packaged startup, and dependency compatibility.
