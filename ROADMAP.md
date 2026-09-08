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
- [x] r42 evidence-only caller timing text report.
- [x] r43 deterministic evidence-only JSON artifact.
- [x] r44 practical offline CLI.
- [x] r46 deterministic multi-artifact evidence bundle.
- [x] r47 deterministic human-readable TSV report.
- [x] r48 deterministic bundle summary.
- [x] r49 deterministic diff between validated bundle-summary artifacts.
- [x] r50 standalone human-readable HTML report from sanitized evidence bundle.
- [x] r51 local in-report search + exact classification filter + result count/reset, fully standalone/offline.
- [x] r52 visible-subset spreadsheet-safe CSV export plus print-to-PDF; GREEN run 633 and auto-merged.
- [x] r53 live summary of the currently visible filtered evidence subset; GREEN run 638 and auto-merged.
- [x] r54 session-only operator bookmarks, Bookmarked-only review and one-click `Bookmark visible`; exact SHA `ef4ed20f33da2a051cfd5b83144b7dd71de77ec1` passed Forgejo and is in main.
- [ ] r55 local `Export visible JSON` for the exact Search/classification/bookmark-filtered subset, preserving raw visible values/classification/bookmark state without new timing semantics; exact tip awaits gate.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Product-facing offline goal
- Prefer portable reports an operator/engineer can open directly (HTML/TSV/CSV/JSON/print-to-PDF) over more internal microguards while semantic live evidence is unavailable.
- Keep JSON/bundle artifacts as machine-readable source evidence behind those views.
- r54 bookmarks are deliberately session-only: no browser persistence and no server/ECSS write; filtered subsets can be marked in one click before export/print review.
- r55 visible JSON is a local handoff of exactly what the operator is reviewing; it is explicitly raw-evidence-only and does not invent Duration/queue-wait semantics.
- After r55 GREEN, prefer a larger useful correlation/operator improvement or wait for real queue CDR rather than another internal guard layer.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, prefer useful offline evidence/report tooling over endless microguards.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
