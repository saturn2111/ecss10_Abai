# Autonomous changelog — r28 caller timing values

- Confirmed r27 caller timing evidence was Forgejo GREEN and auto-merged into `main` as `d7fb0a7b7fac682e6c2678cc1b51c32be9b87e20`.
- `summarize_caller_timing(...)` now exposes raw `caller_t_ecd_seconds` / `caller_t_dba_seconds` only when one exact caller-ref row has both values and there are no competing incomplete rows.
- Duplicate, mixed, missing or blank-ref evidence keeps both selected values `None`; no heuristic row selection is performed.
- The fields remain raw CDR evidence. The increment does not claim that `T_DBA` is queue wait or that caller `T_ECD` is the final external Duration.
- Added deterministic unit coverage. No live ECSS/112/routing/agent/licensing changes were made and no production secrets/data were added.
