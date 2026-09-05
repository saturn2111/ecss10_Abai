# Autonomous development changelog

## 2026-09-05 — Operator answer-delay evidence classification

- Added deterministic `operator_answer_delay_evidence(...)` classification for exact operator-side `T_DBA` evidence in the offline queue-call analyzer.
- The analyzer now reports positive/zero/invalid operator answer-delay record counts alongside the existing duration evidence, using only exact `CONN_ID == operator_call_ref` matches.
- Evidence states distinguish no answer-delay evidence, one positive record, multiple positive records, one zero record, one invalid record, and mixed/ambiguous records; invalid same-ref input remains `not_evaluated`.
- This does not infer queue timing, logical call identity, operator identity, or alter the existing fail-closed `T_ECD` duration-selection rules.
- Added synthetic regression coverage for mixed evidence and every deterministic answer-delay classification state.
- No ECSS production configuration or live 112 state was changed. The real captured queue CDR remains required for final live mapping.

## 2026-09-05 — Operator duration evidence classification

- Added deterministic `operator_duration_evidence(...)` classification to the offline queue-call analyzer.
- Evidence states distinguish no operator duration evidence, one positive record, multiple positive records, one zero record, one invalid record, and mixed/ambiguous records.
- The classifier uses only exact operator `CONN_ID == operator_call_ref` record counts already exposed by the analyzer; it does not infer queue membership, logical call identity, operator identity, or choose a duration beyond existing fail-closed rules.
- Added synthetic regression coverage for every classification state and for invalid same-ref input (`not_evaluated`).
- No ECSS production configuration or live 112 state was changed. The real captured queue CDR remains required for final live mapping.

## 2026-09-05 — Operator duration evidence counts

- Added explicit `operator_positive_duration_record_count`, `operator_zero_duration_record_count`, and `operator_invalid_duration_record_count` fields to the offline queue-call analyzer.
- Counts are derived only from exact operator `CONN_ID == operator_call_ref` records and classify parsed `T_ECD` as positive, zero, or unavailable/invalid.
- The new fields are descriptive evidence only: they do not infer a logical call id, queue membership, operator identity, or choose a duration beyond the existing fail-closed selection rules.
- Added synthetic regression coverage for mixed positive/zero/invalid operator records plus partial/invalid ref cases.
- No ECSS production configuration or live 112 state was changed. The real captured queue CDR is still required for final live mapping.

## 2026-09-05 — Exact-ref uniqueness flags

- Added explicit `caller_ref_unique`, `operator_ref_unique`, and `both_refs_unique` fields to the offline queue-call analyzer.
- Each flag is derived only from exact `CONN_ID == call_ref` record counts; one exact record is unique, zero or multiple records are not.
- Invalid/missing/same-ref input fails closed with all uniqueness flags false.
- Existing duration-selection logic and descriptive `correlation_evidence` semantics are unchanged; the new booleans expose evidence without inferring queue membership or a logical call relationship.
- Added synthetic regression tests for unique, duplicate, partial, and invalid-ref cases.
- No ECSS production configuration or live 112 state was changed. The real captured queue CDR is still required for final live mapping.

## 2026-09-05 — Exact-ref correlation evidence state

- Added deterministic `correlation_evidence` to the offline queue-call analyzer, derived only from exact caller/operator `CONN_ID == call_ref` record counts.
- Evidence states distinguish `both_refs_unique`, `both_refs_present_with_duplicates`, `partial_ref_match`, and `no_ref_match`; invalid/missing/same-ref input reports `not_evaluated`.
- The field is descriptive evidence only: it does not infer a shared logical call id, operator identity, queue membership, or duration correctness.
- Added synthetic regression tests for unique, duplicate, partial, no-match, and invalid-ref evidence states.
- No ECSS production configuration or live 112 state was changed. The captured real queue CDR is still required for final live mapping.

## 2026-09-05 — Explicit CDR correlation evidence

- Extended the offline queue-call analyzer with `caller_ref_matched`, `operator_ref_matched`, and `both_refs_matched` so reports distinguish observed evidence from inferred correlation.
- The new fields are derived only from exact `CONN_ID == call_ref` matches; no logical call id, operator identity, or missing caller record is guessed.
- Added synthetic tests for complete two-ref evidence, missing operator evidence, operator-only evidence, blank refs, and same-ref ambiguity.
- Existing operator-duration selection semantics remain unchanged: an exact unambiguous operator record may expose `T_ECD`, while the evidence flags separately show whether both captured refs were present.
- This remains offline tooling only. No ECSS production configuration or live 112 state was changed, and the real captured queue CDR is still required for final live mapping.

## 2026-09-05 — Non-finite CDR metric guard

- Hardened `_to_int(...)` so non-finite numeric strings such as `inf`/`-inf` fail closed instead of raising `OverflowError` during offline CDR parsing.
- Non-finite `T_ECD` is treated as unavailable and cannot confirm operator duration; non-finite `T_DBA` is not exposed as answer delay.
- Added synthetic regression tests for infinite duration and answer-delay inputs while preserving valid positive duration handling.
- This remains offline correlation tooling only. No ECSS production configuration or live 112 state was changed, and a real captured queue CDR is still required for final live mapping.

## 2026-09-05 — Invalid operator T_ECD selection guard

- Hardened the offline queue CDR analyzer so a single operator record with malformed, blank, or negative `T_ECD` is not selected as the duration source.
- Such input now reports deterministic `selection_reason=invalid_operator_t_ecd`, leaves `selected_operator_conn_id`/duration unavailable, and cannot confirm operator duration.
- Added synthetic regression coverage for negative and malformed operator `T_ECD` while preserving valid positive duration behavior.
- This remains offline correlation tooling only. No ECSS production configuration or live 112 state was changed, and the real queue CDR is still required for final live mapping.

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
