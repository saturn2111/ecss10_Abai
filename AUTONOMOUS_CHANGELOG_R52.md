# Autonomous changelog r52

- Added `Export visible CSV` to the standalone CDR evidence HTML report.
- Added `Print visible` so the same currently filtered evidence subset can be printed or saved to PDF through the browser.
- Export/print include only rows visible after local text/classification filtering and are disabled when the filter leaves zero rows.
- Print styling hides controls and keeps hidden rows excluded from paper/PDF output.
- CSV is generated fully offline in the browser from already embedded sanitized evidence.
- CSV quoting is applied and spreadsheet formula prefixes (`=`, `+`, `-`, `@`) are neutralized.
- HTML report schema is now `ecss-cdr-evidence-html-report-v4`.
- Raw T_ECD/T_DBA remain evidence-only; no queue-wait or final-Duration semantics are inferred.
- Added regression coverage; no live ECSS/112/agent/routing changes were made.
