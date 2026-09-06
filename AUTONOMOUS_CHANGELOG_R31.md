# Autonomous changelog — r31 caller ref whitespace guard

- Confirmed r30 commit `3cafa0dc87045af8d52b60222bd6c15fd0be8d84` was Forgejo GREEN and auto-merged into `main` as `279c9acdef2345d08be411778c18f6ec8da01383`.
- `summarize_caller_timing(...)` now rejects surrounding whitespace on a nonblank supplied caller ref instead of silently trimming and changing the exact evidence identifier before matching `CONN_ID`.
- Whitespace-only refs remain `not_evaluated`; exact nonblank refs keep existing behavior.
- Added regression tests for padded refs, whitespace-only input and exact refs.
- This remains offline evidence tooling only: it does not infer queue membership, queue wait, logical call identity or external Duration semantics and performs no live ECSS/112 changes.
