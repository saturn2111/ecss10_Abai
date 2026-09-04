# Autonomous development changelog

## 2026-09-04 — CDR distinct call-ref guard

- Hardened the offline queue CDR analyzer so caller and operator `call_ref` values must be present and distinct.
- Blank refs fail closed with `missing_call_ref`.
- Equal caller/operator refs fail closed with `ambiguous_same_call_ref` and never confirm operator duration.
- Added regression tests for both ambiguity cases while preserving existing CSV/duration tests.
- This does not change ECSS production configuration and does not add new factual conclusions about the live 112 queue call; real queue CDR remains required for final duration mapping.
