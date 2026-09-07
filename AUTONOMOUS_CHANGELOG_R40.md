# Autonomous Changelog — R40

Date: 2026-09-07

- Added fail-closed `caller_has_any_timing_records` over exact non-negative complete/incomplete caller timing counts.
- Added regression coverage for no evidence, complete-only, incomplete-only, mixed, non-exact types and negative values.
- Exposed the diagnostic in `summarize_caller_timing` without weakening existing raw `T_ECD/T_DBA` evidence gating.
- Recorded that r39 was auto-merged after the local gate.
- No queue-membership, `T_DBA`, final Duration or logical-call-id semantics are inferred, and no live ECSS/112/agent/licensing/routing changes were made.
- No credentials or subscriber-sensitive raw production CDR were added.
