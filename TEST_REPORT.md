# Validation · 4.1.0

**715 automated tests pass on Python 3.12**, including 29 new named-probability tests, 68 custom-command tests, and the existing 618 regression tests. One upstream discord.py warning concerns Python's deprecated audioop module; the suite has no failures.

The real Discord command tree serializes nine global commands: /roll, /avatar, /wallet, /wallet-add, /wallet-remove, /wallet-transfer, /wallet-manage, /builder, and /custom. Named custom commands are separately scoped to their server and restored from published definitions. Their callbacks use current definitions; global Avatar and wallet commands remain intact.

## New workflows verified

- Exact named probabilities total 100%, preserve four-place decimal precision through editing, and select the correct distribution at every tested ticket boundary. Invalid/incomplete totals are rejected without silent normalization. Public output and replay receipts contain only the selected name, even when Rigger changes it.
- Named probability types coexist with 1d5, all six 6d20 values, and a separate modified 1d20. Tests cover the actual Add outcome picker, modal, editing, publishing, slash callback, private validation errors, revoked permissions, all six numeric Rigger modes, named Force status, conditional branches, replay, duration persistence, and compatibility with previous weighted-table output.
- Independent named groups: 1d5, all six outcomes of 6d20, and a separate 1d20 with a visible modifier.
- Exact weighted-ticket boundaries, decimal/percentage inputs, normalization, invalid odds, protected built-in names, bounded templates, and safe validation of malformed entries.
- Conditional rolls using final controlled numeric/named outcomes, skipped descendants, stable references after renames, and rejected invalid reorder/deletion dependencies.
- Draft/live separation, explicit publishing, optimistic revision conflicts, reversible archives, server and bot-owner isolation, and real server owner/admin/moderator permissions.
- All numeric Rigger modes on custom steps, text-face controls, weighted-name presets, stacked whole-template/specific-step priority, independent scopes, once-per-character counters, skipped conditional counters, permanent rules, restart persistence, duplicate receipts, and rollback on final-write failure.
- Shop quantity review and confirmation, current-price checks, insufficient funds, foreign-wallet rejection, inventory tracking, cancellation, durable duplicate protection, and transactional balance/ledger/inventory rollback. Two concurrent database connections cannot spend the same funds twice.
- Actual Discord views, dropdowns, buttons, modals, payload serialization, private/public replies, stale forms, revoked permissions, owner/server guards, normal draft previews without rig consumption, Unicode/escaped text sizes, dynamic slash callbacks, and recovery from slash-sync failure through /custom.

## Existing regressions retained

Avatar nation/family/tribe/control boundaries, strict bending above 60, Nomad-only element d3, all six individual stat controls, Bending Strength only for benders, every Rigger mode/percentage/duration, hidden extra candidates, saved receipts, legal dice, custom faces, modifiers, private control access, wallet permissions, moderator transfers, migration, persistence, and atomic transactions all remain passing.

Source and rebuilt bot.pyz pass offline command validation. The release also validates in an isolated directory containing only Dockerfile, requirements.txt, railway.toml, and bot.pyz, matching the Railway upload layout. The runtime bundle contains all 18 package modules and does not depend on flattened loose source files.

## Verification boundary

Tests use deterministic/random local dice as appropriate, temporary SQLite databases, actual discord.py classes, and mocked Discord transport. They do not send game messages or spend player currency in live servers. Local tests do not establish live deployment status. Railway build/startup and Discord Gateway reconnection are verified separately after publishing the release. A real player clicking the new Discord panels has not been tested through a signed-in Discord browser session.
