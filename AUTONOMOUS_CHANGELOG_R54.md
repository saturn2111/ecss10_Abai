# Autonomous changelog r54

Date: 2026-09-08

- Confirmed r53 exact SHA `d9dbf9e339e96f3ec3cf591603edc86e42c16fdb` passed Forgejo run 638 and auto-merged into `main` as `11b3441961d366d37affa1f1d9715d91ef9daa57`.
- Added a standalone operator-review report on top of the verified visible-summary report.
- Each evidence row receives a session-only bookmark checkbox; `Bookmarked only` shows the marked subset and `Clear bookmarks` resets the current review session.
- Added `Bookmark visible`: after Search/classification filtering, one click marks every row in that current base subset so an operator does not have to click each evidence row individually.
- Bookmarks are intentionally not written to localStorage, a server, ECSS or any external service.
- Existing search/classification filters, visible item count, live summary, CSV export and print continue to operate on the actual visible subset; raw `T_ECD/T_DBA` remain evidence only and are not relabelled as queue wait/final Duration.
- Added regression coverage for the review controls, filtered bulk-bookmark behavior, session-only boundary and unchanged timing-semantics warning.
- No live 112/agents/routing/licensing changes or production CDR/credentials were added.
- Exact final r54 branch tip still requires Forgejo PASS before it is considered verified or merged.
