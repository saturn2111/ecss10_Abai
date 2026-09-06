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
- [x] r27 exact caller-ref timing completeness evidence; Forgejo GREEN and auto-merged as `d7fb0a7b7fac682e6c2678cc1b51c32be9b87e20`.
- [x] r28 surface raw T_ECD/T_DBA values only when exactly one complete caller-ref row exists and no competing incomplete row; Forgejo GREEN and auto-merged as `8738b32dafd3223d85e992bbe6cfa837d652c419`.
- [x] r29 require exact string caller refs at the offline evidence boundary; Forgejo GREEN and auto-merged as `77ac711877bdb6786e213f976c9eab33716e3f14`.
- [ ] r30 require exact `CdrRecord` values at the caller timing evidence boundary; awaiting Forgejo gate.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, stay offline-only: correlation tooling, tests and documentation.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
