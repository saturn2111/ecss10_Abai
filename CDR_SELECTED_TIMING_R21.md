# Offline selected-operator timing projection — r21

This increment is intentionally limited to already-selected exact operator CDR evidence.

`selected_operator_timing_values(record)` returns `(T_ECD, T_DBA)` only when both parsed fields are present on that already-selected `CdrRecord`. A real zero is preserved as valid evidence. Missing selection or either missing metric returns `None`.

The helper does **not** select a CDR row, infer a logical `call_id`, infer queue wait time from `T_DBA`, choose a production `Duration` source by itself, or make any claim about the still-unavailable real queue CDR.

Final queue-call mapping still requires the actual `cdr_dp_abai_default_20260903_17_00_00_p.csv` and exact comparison of both listener `call_ref` values with CDR `CONN_ID`.
