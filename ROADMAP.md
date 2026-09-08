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
- [x] r42-r50 evidence-only text/JSON/CLI/bundle/TSV/summary/diff/standalone HTML foundation.
- [x] r51 local in-report search + exact classification filter + result count/reset.
- [x] r52 visible-subset spreadsheet-safe CSV export plus print-to-PDF.
- [x] r53 live summary of the currently visible filtered evidence subset.
- [x] r54 session-only operator bookmarks, Bookmarked-only review and one-click `Bookmark visible`.
- [x] r55 local `Export visible JSON` for the exact Search/classification/bookmark-filtered subset; exact SHA `7e179cf42a5830a0fa3e9a9c05547e9eecadc7b7` passed Forgejo run 677 and is merged.
- [ ] r56 local `Export visible Markdown` handoff for the exact currently visible subset, including active filter context and raw-evidence disclaimer, with no new timing semantics; exact final tip awaits gate.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Product-facing offline goal
- Prefer portable reports an operator/engineer can open or hand off directly (HTML/TSV/CSV/JSON/Markdown/print-to-PDF) over more internal microguards while semantic live evidence is unavailable.
- Keep JSON/bundle artifacts as machine-readable source evidence behind those views.
- Bookmarks remain session-only: no browser persistence and no server/ECSS write.
- r55 visible JSON is a machine-friendly local handoff of exactly what the operator is reviewing.
- r56 Markdown is a human-friendly ticket/chat/service-note handoff of the same current visible subset and explicitly preserves raw `T_ECD/T_DBA` labels without inventing Duration/queue-wait semantics.
- After r56 GREEN, prefer a larger useful correlation/operator improvement or wait for real queue CDR rather than another internal guard layer.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, prefer useful offline evidence/report tooling over endless microguards.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
