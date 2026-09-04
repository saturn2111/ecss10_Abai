# Autonomous development changelog

## 2026-09-04 — CDR distinct call-ref guard

- Hardened the offline queue CDR analyzer so caller and operator `call_ref` values must be present and distinct.
- Blank refs fail closed with `missing_call_ref`.
- Equal caller/operator refs fail closed with `ambiguous_same_call_ref` and never confirm operator duration.
- Added regression tests for both ambiguity cases while preserving existing CSV/duration tests.
- This does not change ECSS production configuration and does not add new factual conclusions about the live 112 queue call; real queue CDR remains required for final duration mapping.

## 2026-09-04 — Ambiguous operator-record guard

- Removed the offline analyzer heuristic that selected the largest positive `T_ECD` when several positive records shared the operator `call_ref`.
- Multiple positive operator records now fail closed as `ambiguous_multiple_positive_operator_records`; multiple non-positive operator records fail closed as `ambiguous_multiple_operator_records`.
- Duration is confirmed only when the captured operator ref maps unambiguously to one positive operator record.
- Added synthetic regression coverage for both multiple-record ambiguity cases.
- No ECSS production change was made and no new live 112/CDR conclusion is asserted without the real CDR file.
