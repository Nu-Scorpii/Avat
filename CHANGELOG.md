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
