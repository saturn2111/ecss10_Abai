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
- [x] r55 local `Export visible JSON` for the exact Search/classification/bookmark-filtered subset; run 677 GREEN.
- [x] r56 local `Export visible Markdown` handoff for the exact currently visible subset; exact SHA `b00aadfa8059a69a1374c4bfd07cefa72d689ef6` passed Forgejo run 700 and is merged.
- [x] r56 documentation state-sync also auto-merged into canonical main `29aa9affd04471fe934cfcfb9a4d7b83d6b11116`; do not repeat it.
- [ ] Validate queue-call CDR mapping against a real sanitized CDR captured from a confirmed live queue call.
- [ ] Only after evidence, define which field/row maps to external `Duration` and whether any timing field has queue-wait semantics.

## Product-facing offline goal
- Verified portable operator handoff includes HTML/TSV/CSV/JSON/Markdown/print-to-PDF plus session-only bookmarks and visible-subset filtering.
- Keep JSON/bundle artifacts as machine-readable source evidence behind those views.
- Bookmarks remain session-only: no browser persistence and no server/ECSS write.
- Do not add another small presentation guard merely to keep activity moving; the next offline increment should materially improve correlation/operator workflow.
- Semantic correlation is deliberately waiting for real sanitized queue CDR evidence instead of inventing `Duration`/queue-wait meaning.

## Rules
- No live production changes without current factual data and explicit need.
- PROJECT_STATE is source of truth; do not redo verified licensing/VRRP/Mnesia/test2000/agents/route112 work.
- While live CDR/phones are unavailable, switch effort to other projects instead of producing endless microguards.
- Never commit credentials, API keys, JWTs or subscriber-sensitive raw production data.
