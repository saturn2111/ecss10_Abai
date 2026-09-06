# Autonomous changelog — r27 exact caller timing evidence

- Confirmed r26 exact-Decimal CDR timing parsing passed Forgejo and auto-merged into `main` as `cb8b670bf2d7447425597eaf84b3a70b4bc7ca98`.
- Added an offline caller-side timing-completeness projection using only exact `CONN_ID == caller_call_ref` records.
- The helper reports complete/incomplete caller timing row counts and a deterministic evidence label; blank refs fail closed as `not_evaluated`.
- Count classification rejects bool/non-integer and negative manually supplied counts.
- The helper does not select final duration, infer a shared logical call id, infer queue membership/operator identity, or interpret `T_DBA` as queue wait time.
- Added standard-library regression tests for all evidence states, invalid count shapes, exact-ref filtering, mixed complete/incomplete rows and blank refs.
- No live ECSS production configuration or 112 routing/agent state was changed. The captured real queue CDR remains required for final live mapping.
