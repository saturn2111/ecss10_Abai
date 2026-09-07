# Autonomous changelog — r47

- Confirmed r46 exact SHA `db4ad3943d1273fab4a4e4b7962180907619d6b4` passed Forgejo GREEN run 565 and auto-merged into `main` as `da95d849aeedefb8c35dafc4a59d311a706fd28f`.
- Added `tools/cdr_evidence_bundle_report.py` to render verified multi-artifact bundles as deterministic human-readable TSV without semantic inference.
- Ambiguous raw timing remains `n/a`; label/caller-ref order is preserved and the bundle semantic warning remains explicit.
- Added regression tests for deterministic order, ambiguous timing and schema rejection.
- No live ECSS, route 112, agent, licensing, VRRP or Mnesia changes were performed.
