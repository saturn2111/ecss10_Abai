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
- [x] r35-r41 fail-closed timing evidence diagnostics through Forgejo GREEN.
- [x] r42 evidence-only caller timing text report; fixed SHA GREEN run 535.
- [x] r43 deterministic evidence-only JSON artifact; GREEN run 548.
- [x] r44 practical offline CLI for sanitized CDR + exact caller ref; GREEN run 553.
- [x] r45 canonical state synchronization; auto-merged into `main` as `2b740529fd13811b00eb76a93aff6675fdc77985`.
- [ ] r46 deterministic multi-artifact evidence bundle using repeated sanitized CDR/caller-ref items.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, prefer useful offline evidence/report tooling over endless microguards.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
