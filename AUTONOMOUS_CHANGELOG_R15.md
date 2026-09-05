# Autonomous development changelog — r15

## 2026-09-05 — Selected operator timing completeness evidence

- Added `selected_operator_has_complete_timing` to the offline queue-call analyzer.
- The flag describes only the exact operator record already selected by the existing fail-closed `T_ECD` rules and is true only when that same record contains parsed `T_ECD` and `T_DBA`.
- Missing `T_DBA`, ambiguous multiple-positive operator records, partial exact-ref evidence, and invalid same-ref input all fail closed to `false`.
- The field does not select a new duration source, infer logical call identity, infer queue membership, or treat `T_DBA` as queue wait time.
- Added synthetic regression coverage for complete, incomplete, ambiguous, partial, and invalid-ref cases.
- No live ECSS production configuration was changed. The real `cdr_dp_abai_default_20260903_17_00_00_p.csv` remains required before final queue-call Duration/finished mapping is claimed.

Canonical `PROJECT_STATE.md` remains authoritative; its current live-data blocker and next action are unchanged.