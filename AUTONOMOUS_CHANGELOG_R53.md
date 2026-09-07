# Autonomous changelog r53

Date: 2026-09-08

- Confirmed r52 exact SHA `96090992735d5b305a89186fbddf743bf3a58495` passed Forgejo run 633 and auto-merged into `main` as `5c6d5322f471666adc2c95982b0d2b79c495e76d`.
- Added a new standalone operator report with a live summary of only the currently visible evidence rows after the existing search/classification filtering.
- The summary shows visible item count, total CDR records, complete/incomplete timing-row counts and exact evidence-classification counts.
- Recalculation happens locally in the browser; no ECSS/server call is required.
- Raw `T_ECD/T_DBA` remain evidence only and are not relabelled as queue wait or final Duration.
- Added regression coverage for filter wiring, visible-row aggregation and semantic-boundary text.
- No live ECSS/112/agent/routing/licensing changes, credentials or subscriber-sensitive production CDR were added.
- Exact-SHA Forgejo GREEN remains required before r53 is considered verified.
