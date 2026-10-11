# Validation · 3.3.0

**335 automated tests pass on Python 3.12**, including 62 new tests for percentage strength, stacking, individual stats, and active-rig management. Source and bundle startup checks validate the real two-command tree: `/roll` and `/avatar`.

New coverage checks good/bad strength from 1–100%, numeric rounding, optional percent-sign input, invalid percentages, signed dice and bonuses, highest/lowest selection, sparse weighted numeric faces, legal results, monotonic strength, and no extra random draws for luck.

Combined Avatar coverage stacks IQ, nation, bending, Nomad element, and all six stat forces in one character. It mixes stat force/shift/luck, checks specific luck overriding broader luck and exact force winning last, preserves other players and command scopes, clears impossible/skipped rigs individually, retains lasting luck, and checks Nomad bending transitions at 60/61 after percentage changes.

Storage tests cover old single-setting migration, default strength for old luck, persistent stacks, stable rule IDs, duplicate Apply/removal/complete-character receipts, creator namespaces, individual/player/all clearing, corrupt individual entries, atomic rollback of all consumption after write failure, and the bounded receipt cache.

Private UI tests cover owner-only DM entry, verified non-owner targeting across servers, engine and button/select/modal guards, percentage forms, drafts versus live state, active counts, pagination, filtering, editing/removal, consumed-rule refresh, stale/expired forms, reopening, and real Discord payloads. A full 100-rig list fits select, row, option, and embed limits.

Existing regressions retain every Avatar range and conditional branch, strict bending above 60, custom dice parsing, text faces, exact totals, impossible requests, solver limits, public message sizing and mention escaping, minimal Gateway intents, command synchronization, and obsolete-command cleanup.

Tests use deterministic dice and mocked Discord transport. They do not send game messages to players. Railway build/startup and the actual Discord connection are verified separately after deployment. The private panel requires the installed bot, correct creator user ID, and permission to DM it.
