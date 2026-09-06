# Autonomous changelog — r29 caller-ref type guard

- Confirmed r28 passed Forgejo and was auto-merged into `main` as `8738b32dafd3223d85e992bbe6cfa837d652c419`.
- `summarize_caller_timing(...)` now requires `caller_call_ref` to be an exact built-in string; malformed values fail closed with an explicit type error instead of relying on accidental `.strip()` behavior or coercion.
- Blank strings retain the existing `not_evaluated` result with no selected timing values.
- Added deterministic offline regression tests. No queue-wait, logical-call-id or external-duration semantics are inferred.
- No live ECSS, 112 routing, agent, licensing or subscriber configuration was changed and no production CDR/credentials were added.
