# Autonomous changelog r55

- Confirmed r54 operator bookmarks exact SHA `ef4ed20f33da2a051cfd5b83144b7dd71de77ec1` passed Forgejo and is in current main.
- Added `Export visible JSON` to the standalone offline CDR evidence review report.
- Export uses exactly the currently visible rows after Search, classification and Bookmarked-only filtering; hidden rows are not included.
- Each exported row preserves current classification, session bookmark state and visible evidence-cell text while excluding the runtime Review checkbox column.
- Artifact schema is `ecss-cdr-evidence-review-visible-v1` with explicit `raw-visible-values-only` evidence semantics.
- JSON is produced locally in the browser with `Blob`/object URL and fixed filename `ecss-cdr-visible-evidence.json`; no fetch, localStorage, server/ECSS write or production access is added.
- `T_ECD`/`T_DBA` remain raw evidence and are not renamed or interpreted as queue wait/final Duration.
- Added regression coverage for visible-only export structure, local object-URL cleanup and absence of persistence/network/semantic relabeling.
- Final r55 exact branch tip requires Forgejo GREEN before it is treated as verified or merged.
