# Autonomous Changelog — ECSS10 ДП Абай r37

## 2026-09-07 — incomplete caller timing diagnostic

- Added fail-closed `caller_has_incomplete_timing_records` for exact caller-ref timing evidence counts.
- `summarize_caller_timing` now exposes whether at least one exact-ref timing row is incomplete while preserving existing unique-complete/raw T_ECD/T_DBA gating.
- Added `unittest` coverage for zero/complete/incomplete/mixed counts and invalid types/negative values.
- No queue-membership, `T_DBA`, final `Duration` or logical-call-id semantics are inferred; no live ECSS/112/agent/routing/licensing changes were made.
