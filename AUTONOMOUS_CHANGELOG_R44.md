# Autonomous Changelog r44

- Recorded verified r43 deterministic JSON evidence artifact (Forgejo run 548).
- Added a practical offline CLI for sanitized CDR + exact caller ref with deterministic text/JSON output.
- Reuses verified parser/report semantics; ambiguous timing remains fail-closed and no queue/final-duration meaning is inferred.
- Missing/invalid input returns nonzero without contacting production ECSS.
- No route 112, agents, licensing, VRRP, Mnesia or live production changes.
