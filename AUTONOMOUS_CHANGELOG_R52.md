# Autonomous changelog r52

- Added `Export visible CSV` to the standalone CDR evidence HTML report.
- Export includes only rows currently visible after local text/classification filtering.
- CSV is generated fully offline in the browser from already embedded sanitized evidence.
- CSV quoting is applied and spreadsheet formula prefixes (`=`, `+`, `-`, `@`) are neutralized.
- Raw T_ECD/T_DBA remain evidence-only; no queue-wait or final-Duration semantics are inferred.
- Added regression coverage; no live ECSS/112/agent/routing changes were made.
