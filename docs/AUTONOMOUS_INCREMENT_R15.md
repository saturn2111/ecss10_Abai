# Autonomous increment r15 — selected operator timing completeness

Date: 2026-09-05

## Offline tooling change

`tools/cdr_queue_analyzer.py` now reports `selected_operator_has_complete_timing` for the exact operator record already chosen by the existing fail-closed `T_ECD` selection rules.

The flag is `true` only when that already-selected exact `CONN_ID == operator_call_ref` record contains both parsed `T_ECD` and parsed `T_DBA`. If no record is selected because the evidence is ambiguous, or if either metric is unavailable/invalid, the flag is `false`.

## Boundary

This field does not choose a new duration source, does not infer a logical call id or queue membership, does not identify an operator beyond the supplied exact operator `call_ref`, and does not claim that `T_DBA` is queue wait time. Existing duration selection and `operator_duration_confirmed` semantics are unchanged.

Synthetic tests cover a selected complete row, a selected row with missing `T_DBA`, an ambiguous multiple-positive-record case, partial exact-ref evidence, and invalid same-ref input.

No ECSS production configuration, live 112 route, queue, agent, license, VRRP, Mnesia, or phone state was changed. The real `cdr_dp_abai_default_20260903_17_00_00_p.csv` remains required for final live queue-call mapping.

## Project-state handoff

Canonical `PROJECT_STATE.md` remains the source of truth. Its current next action remains unchanged: obtain the real queue CDR and correlate its `CONN_ID` values with the captured caller/operator `call_ref` values before finalizing Duration/finished mapping.