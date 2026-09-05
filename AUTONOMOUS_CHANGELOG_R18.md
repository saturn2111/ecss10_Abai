# Autonomous development changelog — r18

## 2026-09-06 — Selected operator missing timing fields

- Added `selected_operator_missing_timing_fields(...)` as a deterministic offline projection for an already-selected exact operator CDR row.
- The helper reports only missing raw timing columns: `T_ECD`, `T_DBA`, both, or none; zero values count as present evidence.
- `None` selection returns no field list and does not invent a record or correlation.
- The helper does not infer queue membership, logical call identity, operator identity, queue wait time or a duration source.
- Added synthetic tests for complete, one-field-missing, both-fields-missing and zero-value cases.
- No ECSS production configuration, queue, route, agent, license, VRRP, Mnesia or phone state was changed. The captured real queue CDR is still required for final live mapping.
