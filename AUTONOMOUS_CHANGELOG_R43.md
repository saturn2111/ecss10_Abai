# Autonomous Changelog — ECSS10 r43 deterministic timing JSON

- Confirmed r42-fix exact SHA `a2f84d4ad4bf713d84736590ede150f594f58819` passed Forgejo GREEN run 535 and auto-merged as `7464a3c1ba9558a2923a7b2a5dc7d39ae94bb6fc`.
- Added `build_caller_timing_report_json(...)` on top of the same verified caller-timing summary used by the text report.
- JSON output is deterministic (`sort_keys`, compact separators, ASCII-safe) and preserves raw timing values only for unambiguous evidence; competing/ambiguous timing remains `null`.
- Added regression tests for unique complete evidence, competing rows and deterministic serialization.
- The artifact keeps the explicit warning that queue membership, queue wait, logical call identity and final Duration are not inferred.
- No live ECSS/112/agent/routing/licensing changes or production credentials were introduced.
