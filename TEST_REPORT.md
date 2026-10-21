# Validation · 4.1.1

All 715 automated tests pass on Python 3.12. They cover custom dice, Avatar creation, Bending Strength, wallets, transfers, shops, FAQs, the server builder, exact named probabilities, dynamic slash commands, permissions, persistence, duplicate requests, and transaction rollback.

The real Discord command tree serializes exactly nine global commands: `/roll`, `/avatar`, `/wallet`, `/wallet-add`, `/wallet-remove`, `/wallet-transfer`, `/wallet-manage`, `/builder`, and `/custom`. Published custom commands are scoped to their own server and restored at startup.

Public and staff-facing privacy checks cover command payloads, builder help, previews, character results, startup logs, error messages, and permission failures. Player and moderator output contains only the features and results available to that audience. Server owners and administrators do not receive access merely because of their server permissions.

Exact named probabilities must total 100%, preserve up to four decimal places, and expose only the selected name. Mixed character templates support independent `1d5`, `6d20`, modified `1d20`, named outcomes, and conditional branches. FAQ and shop workflows use private panels, recheck permissions, reject stale forms, and preserve atomic wallet behavior.

Avatar regression coverage includes nation, family, tribe, village control, the strict bending threshold, Nomad-only element selection, non-bender combat, six individual stats, and Bending Strength for benders only. Existing saved data and older character receipts remain compatible.

Source, rebuilt `bot.pyz`, and an isolated Railway layout containing only `Dockerfile`, `requirements.txt`, `railway.toml`, and `bot.pyz` pass offline startup validation. Live Railway status and Discord Gateway connection are verified separately after deployment.
