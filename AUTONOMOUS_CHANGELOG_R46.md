# Autonomous changelog — r46

- Confirmed r45 canonical state sync is in `main` as `2b740529fd13811b00eb76a93aff6675fdc77985`.
- Added `tools/cdr_evidence_bundle.py`, a deterministic schema-versioned JSON bundle over multiple sanitized CDR/caller-ref evidence items using the already verified parser and caller timing JSON report.
- Added regression tests for stable JSON, preservation of ambiguous timing as `null`, item ordering and duplicate-label rejection.
- The bundle remains evidence-only: it does not infer queue membership, queue wait, logical call identity, final external Duration or recording semantics.
- No live ECSS, route 112, agent, licensing, VRRP or Mnesia changes were made.
