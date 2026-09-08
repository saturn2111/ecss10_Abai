# Autonomous changelog r54

Date: 2026-09-08

- Confirmed the base r54 session-only bookmark review passed the local gate and auto-merged into current `main` as `d9ff2dd1f1b206080f00064eafdd0ab0bfac5148`.
- The older `ai/cdr-html-bookmarks-r54` subsequently diverged from main, so it is intentionally abandoned rather than force-merged or layered further.
- Created clean follow-up branch `ai/cdr-html-bookmark-visible-r54` directly from current main and reapplied only the still-unmerged operator improvement.
- Added `Bookmark visible`: after Search/classification filtering, one click marks exactly the current base-visible subset instead of requiring individual ★ clicks.
- The bulk action is disabled when no evidence rows are visible and then composes with existing `Bookmarked only`, visible summary, CSV export and Print/PDF behavior.
- Bookmarks remain session-only: no localStorage, server, ECSS or external-service writes are introduced.
- Regression coverage locks the exact filtered-subset action, empty-subset disable behavior and unchanged evidence-only timing semantics; raw `T_ECD/T_DBA` are not relabelled as queue wait/final Duration.
- No live 112/agents/routing/licensing changes or production CDR/credentials were added.
- Exact final clean-branch SHA still requires Forgejo PASS before this follow-up is considered verified or merged.
