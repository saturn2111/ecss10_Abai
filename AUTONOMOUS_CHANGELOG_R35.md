# Autonomous changelog — r35 competing caller timing evidence diagnostics

- Confirmed r34 state sync is already in verified `main` as `56ab687a154a4b5447c8463e5651853a1a116b63`; no verified production configuration was revisited.
- Added fail-closed `caller_has_competing_timing_records(...)` for exact caller-ref timing evidence and surfaced the result in `summarize_caller_timing(...)`.
- More than one exact-ref timing row is reported as competing evidence; zero or one row is not. Invalid types and negative counts are rejected.
- Added standard-library `unittest` coverage for no/single, multiple/mixed and invalid count cases.
- No queue-membership inference, `T_DBA` queue-wait meaning, final Duration selection, logical-call heuristic or live ECSS/112 change was introduced. No credentials or raw production CDR were added.
