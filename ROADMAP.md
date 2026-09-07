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
- [x] r42 evidence-only caller timing text report; GREEN run 535.
- [x] r43 deterministic evidence-only JSON artifact; GREEN run 548.
- [x] r44 practical offline CLI; GREEN run 553.
- [x] r46 deterministic multi-artifact evidence bundle; GREEN run 565.
- [x] r47 deterministic human-readable TSV report.
- [x] r48 deterministic bundle summary.
- [x] r49 deterministic diff between validated bundle-summary artifacts; GREEN run 595.
- [x] r50 standalone human-readable HTML report from sanitized evidence bundle; auto-merged into main.
- [ ] r51 local in-report search + exact classification filter + result count/reset, still fully standalone/offline.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Product-facing offline goal
- Prefer portable reports an operator/engineer can open directly (HTML/TSV) over more internal microguards while semantic live evidence is unavailable.
- Keep JSON/bundle artifacts as machine-readable source evidence behind those views.
- After r51 GREEN, prefer printable/exportable selected evidence or a compact operator summary over another internal guard layer.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, prefer useful offline evidence/report tooling over endless microguards.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
