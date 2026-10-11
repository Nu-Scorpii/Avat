# Validation · 3.2.0

273 automated tests pass on Python 3.12. Source and bundled startup checks validate the real Discord command tree: `/roll` and `/avatar` only. Runtime dependency compatibility and the four-file Railway package are checked during release.

Private panel tests cover lower/upper case `!rigger`, owner DM access, server and non-owner rejection, button/select/modal authorization, independent engine guards, draft versus active settings, verified target selection, targeted non-owner Avatar rolls across servers, default owner targeting, command scopes, duplicate Apply, persistence, reopening, stale forms, timeout, private status refresh, and real Discord component/modal serialization within limits.

Avatar boundary tests cover every nation, family, tribe, village, and combat range, plus IQ and six individual stats. Bending values 59, 60, and 61 are checked for all four nations. A value of 60 is non-bender. Only a final Nomad with bending above 60 rolls the element d3; force and luck changes drive the subsequent branch, and no inapplicable die is drawn. No Air element is available.

Existing regressions cover custom numeric and weighted/text faces, exact totals, signed arithmetic, bonuses, keep-high/low, unreachable results, bounded searches, scoped controls, skipped parts, creator-only mutation, request collisions, complete-character receipts, preserved version-3 settings, bounded caches, and atomic rollback after a failed write.

Discord transport tests retain minimal intents and the normal Gateway dispatcher, synchronize the two public commands, clear obsolete server commands, defer before bounded/database work, keep private controls out of public results, escape mentions, obey message-size limits, and reject slash commands in DMs without consuming controls.

The tests use deterministic dice and mocked Discord transport. They do not send game messages to players or prove a live server installation. Live Railway startup is verified separately after deployment. Opening and operating the panel on Discord requires the correct bot installation, creator user ID, and permission to DM the bot.
