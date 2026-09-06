# Autonomous changelog — r30 caller record type guard

- Confirmed r29 (`2bef15c732b4efc63f72957c4a0eb4371cce5539`) was Forgejo GREEN and auto-merged into `main` as `77ac711877bdb6786e213f976c9eab33716e3f14`.
- Hardened `summarize_caller_timing(...)` so its materialized input must contain exact `CdrRecord` values; mappings, strings, `None` and arbitrary objects fail closed with a clear `TypeError`.
- Existing exact-ref selection and raw `T_ECD/T_DBA` evidence semantics remain unchanged for valid records.
- Added regression coverage for malformed record values and one valid exact record.
- This is offline-only tooling: no queue membership, queue-wait, logical-call or external Duration semantics are inferred, and no live ECSS/112 configuration is changed.
