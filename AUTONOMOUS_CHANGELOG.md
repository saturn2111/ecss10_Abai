# Autonomous development changelog

## 2026-09-05 — Negative CDR metric guard

- Hardened offline CDR parsing so negative elapsed-time values in `T_ECD` or `T_DBA` are treated as invalid (`None`) rather than accepted as durations.
- A negative operator `T_ECD` can no longer produce a confirmed queue-call duration; a valid positive duration can still be confirmed while an invalid negative answer delay remains unavailable.
- Added synthetic regression coverage for negative conversation duration and answer delay.
- This is offline correlation tooling only. No ECSS production configuration or live 112 state was changed, and the real captured queue CDR is still required for final live mapping.

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

## 2026-09-04 — Duplicate required CDR column guard

- Hardened the offline CSV loader against duplicate `CONN_ID`, `T_ECD`, or `T_DBA` header names, which `csv.DictReader` could otherwise collapse into one ambiguous value.
- A duplicate required column now raises a deterministic `ValueError` before any queue-call correlation is attempted.
- Added a synthetic regression test using duplicated `T_ECD` and preserved the existing missing-column and call-ref ambiguity coverage.
- This is offline tooling only: no ECSS production configuration, queue, route, agent, license, VRRP, Mnesia, or phone state was changed.
- No new conclusion about the real 112 call duration is asserted; the real captured CDR remains required for final mapping.
