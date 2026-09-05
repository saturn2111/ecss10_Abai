# Autonomous changelog — r21 selected timing values

- Added `tools/cdr_selected_timing.py` with `selected_operator_timing_values(...)`.
- The projection exposes `(T_ECD, T_DBA)` only from an already-selected exact operator `CdrRecord` when both parsed timing fields are present; numeric zero remains valid evidence.
- Missing selection or either missing timing field fails closed to `None`.
- Added synthetic tests for positive timing, zero timing and incomplete/missing evidence.
- Added `CDR_SELECTED_TIMING_R21.md` documenting the evidence boundary and the still-required real queue CDR.
- No live ECSS production state, route, agent, licensing, VRRP, Mnesia or phone configuration was changed.
- The helper does not infer queue wait, logical call identity, final `Duration`, or `CallRecordUrl`.
