# Validation · 3.5.0

**452 automated tests pass on Python 3.12**, including 62 new wallet tests and all previous Avatar, dice, Rigger, percentage, stat, and duration regressions. Source and bundle startup checks validate the real three-command tree: `/roll`, `/avatar`, and `/wallet`.

Wallet coverage checks creator-only naming, all six accepted moderation permissions, denial even for an unprivileged bot creator, server/player/wallet/creator isolation, positive whole amounts, overdrafts, overflow, label limits and uniqueness, capacity, renaming without losing balances, duplicate additions/removals/creation/renames, durable replay protection independent of the dice cache, restart persistence, ordered history and pagination, two database connections, and rollback after failed receipt writes.

UI tests exercise the actual private slash response, empty and populated balance cards, wallet and member selectors, add/remove forms, history pages, creator buttons, current membership checks, bot-account rejection, stale wallet/player forms, moderator revocation, other-viewer/server denial, form/panel expiry, mention escaping, and real Discord view/modal/embed payload limits with the full 25-wallet list. Integration verifies currency operations draw no dice or consume Avatar rigs, and Avatar rolls never change currency balances.

Duration coverage checks finite and permanent settings for force, shift, good/bad luck, and text faces; independent expiration across servers; one use per multi-die custom roll; complete-character and all-stat luck; mixed per-player durations; all six stat rigs with different counters; persistence across restart; migration of old rigs; explicit replenishment versus duplicate Apply; other-player/scope isolation; invalid input; receipt replays; text/overridden luck; skipped branches; impossible requests; corrupt individual counters; and atomic rollback after receipt failure.

Private duration UI tests exercise the actual button and form, entering a duration before a force value, draft versus Apply, live remaining-use display, editing an existing allowance, switching to permanent, owner/server/expired/stale guards, and real modal/view/embed payload limits. Existing 335 regression tests remain passing.

New coverage checks good/bad strength from 1–100%, numeric rounding, optional percent-sign input, invalid percentages, signed dice and bonuses, highest/lowest selection, sparse weighted numeric faces, legal results, monotonic strength, and no extra random draws for luck.

Combined Avatar coverage stacks IQ, nation, bending, Nomad element, and all six stat forces in one character. It mixes stat force/shift/luck, checks specific luck overriding broader luck and exact force winning last, preserves other players and command scopes, clears impossible/skipped rigs individually, retains lasting luck, and checks Nomad bending transitions at 60/61 after percentage changes.

Storage tests cover old single-setting migration, default strength for old luck, persistent stacks, stable rule IDs, duplicate Apply/removal/complete-character receipts, creator namespaces, individual/player/all clearing, corrupt individual entries, atomic rollback of all consumption after write failure, and the bounded receipt cache.

Private UI tests cover owner-only DM entry, verified non-owner targeting across servers, engine and button/select/modal guards, percentage forms, drafts versus live state, active counts, pagination, filtering, editing/removal, consumed-rule refresh, stale/expired forms, reopening, and real Discord payloads. A full 100-rig list fits select, row, option, and embed limits.

Existing regressions retain every Avatar range and conditional branch, strict bending above 60, custom dice parsing, text faces, exact totals, impossible requests, solver limits, public message sizing and mention escaping, minimal Gateway intents, command synchronization, and obsolete-command cleanup.

Tests use deterministic dice and mocked Discord transport. They do not send game messages to players. Railway build/startup and the actual Discord connection are verified separately after deployment. The private panel requires the installed bot, correct creator user ID, and permission to DM it.
