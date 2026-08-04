# CLK 2.4.0 to 2.5.0 Migration

Do not rewrite an active 2.4.0 Run. Finish it under 2.4.0, or start a new 2.5.0
Run with a new baseline and append-only links to preserved receipts.

For a new 2.5.0 Run:

1. Preserve fixed Chains, ordered Levels, full Barriers, topology-fault records,
   role authority, candidate identities, and every accepted 2.4.0 receipt.
2. Freeze one Worker-to-Checker wake binding per pair and preflight direct send,
   task read/list/unarchive, temporary heartbeat, and `PENDING_WAKE` capability.
3. Create exactly one visible `RUN_PATROL_CONVERSATION` and one heartbeat, bound to
   `gpt-5.6-luna+xhigh` and a frozen 10/15/30-minute interval.
4. Version Required CELL/GO/Level sets. Rebuild displayed progress only from current
   D1 and D2 receipts; do not translate delivery positions into accepted progress.
5. Record `DEVICE_CAPACITY_PROFILE` and initial `CUMULATIVE_ENGINEERING_LOAD`; run
   `CELL_CAPACITY_GATE` before every Worker dispatch and re-evaluate at boundaries.
6. Remove task-Pin capability from every method role. Preserve Owner-explicit Pin
   provenance; report Agent or unknown provenance without automatic unpin.
7. Validate a complete `RUN_CONTROL_TRACE` before activating Level work.

The migration adds no new D layer, dynamic Chain, conditional route, general role
message bus, technical patrol authority, device monitor, or product lifecycle gate.
