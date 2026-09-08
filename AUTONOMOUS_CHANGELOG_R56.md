# Autonomous changelog r56 — visible Markdown evidence handoff

- Confirmed r55 visible JSON passed Forgejo run 677 at exact SHA `7e179cf42a5830a0fa3e9a9c05547e9eecadc7b7` and is merged in canonical main.
- Added standalone `cdr_evidence_handoff_report.py` on top of the verified operator review report.
- Added `Export visible Markdown`, exporting exactly the rows visible at click time after Search/classification/Bookmarked-only filters.
- Handoff includes visible item count, active filter context, bookmark-only state, visible table values and per-row bookmark state.
- Markdown explicitly states raw visible evidence semantics and never labels `T_ECD/T_DBA` as queue wait or final Duration.
- Cell escaping protects Markdown table structure from backslashes, pipes and line breaks.
- Export is browser-local via Blob/object URL to `ecss-cdr-visible-evidence.md`; no fetch, localStorage, server/ECSS write or live production access was added.
- Added regression coverage using the verified evidence-bundle schema.
