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
- [x] Fail-closed duration/timing classifications and exact integer parsing through `Decimal`.
- [x] Raw T_ECD/T_DBA values only when exactly one complete caller-ref row exists and no competing incomplete row.
- [x] Exact caller-ref/record/whitespace guards and unique-complete timing evidence.
- [x] r35-r40 fail-closed timing evidence cardinality/presence diagnostics through Forgejo GREEN.
- [x] r41 exact-cardinality `caller_has_single_timing_record`; exact SHA `0a91265d9836332a563f62a01b998b3b6626fff3` GREEN run 521 and auto-merged as `492992a36c65cf0d029f6a31b2c41bb3a125287f`.
- [ ] r42 evidence-only caller timing report: code/tests retained; first exact SHA `f4ca5fddc226f026e070152ce40458f2b0bf6dfa` RED run 534 only because canonical PROJECT_STATE headings were removed. `ai/cdr-timing-report-r42-fix` restores the protected 17-section document structure and awaits a new gate.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, prefer useful offline evidence/report tooling over endless microguards.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
