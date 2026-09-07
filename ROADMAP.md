# Roadmap — ECSS10 ДП Абай

## Verified production foundation — do not repeat
- [x] ECSS 3.18 cluster/licensing baseline, both licence hosts alive.
- [x] VRRP/Mnesia/cluster prerequisites needed for current service.
- [x] Test 2000.
- [x] Agents 1001/1002, queue/group and production route 112.
- [x] ecss-cc-ui/API foundation and observed conversation-event mapping.

## Offline CDR/correlation tooling
- [x] Exact required-header and duplicate-column guards.
- [x] Exact-ref caller/operator correlation evidence.
- [x] Fail-closed duration/timing classifications.
- [x] r26 exact integer parsing through `Decimal` without binary-float precision loss.
- [x] r27 exact caller-ref timing completeness evidence.
- [x] r28 raw T_ECD/T_DBA values only when exactly one complete caller-ref row exists and no competing incomplete row.
- [x] r29-r32 exact caller-ref/record guards and unique-complete timing evidence.
- [x] r33-r34 canonical project-memory synchronization through Forgejo GREEN.
- [x] r35 expose fail-closed `caller_has_competing_timing_records` diagnostics for exact-ref timing evidence without queue/CDR semantic guesses; Forgejo GREEN and auto-merged as `edb6a3a0a13552fbd00605fbcf0a07f4d450ac9c`.
- [ ] r36 synchronize canonical project memory after verified r35; awaiting Forgejo gate.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, stay offline-only: correlation tooling, tests and documentation.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
