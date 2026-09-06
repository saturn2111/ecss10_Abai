# Autonomous changelog — r32 unique complete caller timing evidence

- Confirmed corrected r31 commit `30471948274c55ba60618d430143a3ae30edbb3b` was Forgejo GREEN and auto-merged into `main` as `109c94a1d7ed5e562edc8a01549241c759c7bfea`.
- Added `caller_has_unique_complete_timing_record` to the offline caller timing summary.
- The flag is true only for exactly one complete exact-ref caller row with no competing incomplete row; duplicate, mixed, incomplete, absent and blank-ref cases fail closed to false.
- This is evidence presentation only: it does not infer queue membership, logical call identity, queue wait, final Duration, recording URL or any production ECSS behavior.
- Added standard-library regression tests. No live ECSS/112/agent/routing/licensing changes were made and no production CDR or credentials were committed.
