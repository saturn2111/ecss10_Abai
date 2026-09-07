# Autonomous changelog — r42 evidence-only caller timing report

- Confirmed r41 exact SHA `0a91265d9836332a563f62a01b998b3b6626fff3` passed Forgejo run 521 and auto-merged into `main` as `492992a36c65cf0d029f6a31b2c41bb3a125287f`.
- Added `tools/cdr_timing_report.py` with `build_caller_timing_report(...)`, a deterministic offline renderer over the already verified exact-ref timing summary.
- The report exposes raw `T_ECD/T_DBA` only when the existing summary resolves one complete uncontested caller row; no/multiple/mixed evidence renders timing values as `n/a`.
- Every report carries an explicit warning that queue membership, queue wait, logical call identity and final duration are not inferred from raw fields.
- Added regression coverage for no evidence, one complete row, competing complete rows and mixed complete/incomplete rows.
- First exact r42 SHA `f4ca5fddc226f026e070152ce40458f2b0bf6dfa` received Forgejo RED run 534 because a documentation compaction removed mandatory canonical PROJECT_STATE headings; the validation failure was not bypassed.
- `ai/cdr-timing-report-r42-fix` restores the protected 17-section PROJECT_STATE structure while retaining the report/tests and the same fail-closed evidence semantics.
- No live ECSS, route 112, agent, licensing, VRRP/Mnesia, credential or production-data change was made.
