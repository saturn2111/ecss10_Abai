# Autonomous Changelog r49 — CDR evidence bundle summary diff

- Confirmed r48 exact SHA `b42e2749154f10eea5f49ad75b22e0c6f996a10c` passed Forgejo GREEN and auto-merged into `main` as `9301d2b015d02b190f2583d442d60f30ad93797a`.
- Added `cdr_evidence_bundle_summary_diff.py` to compare two already-sanitized, already-summarized evidence artifacts.
- Output is deterministic JSON with signed deltas for item/record cardinality and exact evidence-classification counts.
- Both inputs fail closed on unknown schema/warning or inconsistent cardinality/counts.
- The diff preserves the evidence-only warning and does not infer queue membership, queue wait, logical call identity or final Duration.
- Added regression coverage; no live ECSS/112/agent/routing/licensing changes were made.
