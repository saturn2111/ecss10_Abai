# Autonomous changelog — r35 exact queue-analyzer ref pair guard

- Confirmed r34 commit `6f1ef85583a2d78fa9ba8d5169a30ccf736bd955` passed Forgejo and was auto-merged into `main` as `56ab687a154a4b5447c8463e5651853a1a116b63`.
- Hardened offline `analyze_queue_call(...)` so caller/operator refs must be exact built-in strings and nonblank refs with surrounding whitespace are rejected instead of silently trimmed.
- Whitespace-only refs remain explicit missing evidence; no logical call id, queue membership, final Duration or `T_DBA` semantics are inferred.
- Added `unittest` regression coverage for type guards, caller/operator padding and blank evidence.
- No live ECSS, 112 route, queue, agent, licensing, VRRP or Mnesia configuration was changed; no credentials or raw production CDR were added.
