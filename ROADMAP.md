# Roadmap — ECSS-10 ДП Абай

`PROJECT_STATE.md` remains the canonical source of truth. This roadmap is only a compact development index and must never override confirmed production facts there.

## Confirmed production baseline — do not repeat

- [x] Licensing and dual license-manager availability.
- [x] VRRP/SIP failover and Mnesia recovery.
- [x] Call-center test 2000.
- [x] Production agents and `Abai_112` queue/IVR/route 112.
- [x] First real 112 queue passage and live conversation-leg observations.

## Offline CDR correlation tooling

- [x] Exact `CONN_ID == call_ref` correlation foundation with fail-closed ambiguity handling.
- [x] Descriptive duration/answer-delay/timing evidence without inventing queue wait or logical-call facts.
- [ ] Pending r16-r25 parser/evidence hardening remains outside verified `main` until Forgejo validates it.
- [ ] r26: deterministic offline helper for mapping a call timestamp to the expected next-hour closed CDR filename; no ECSS access or production mutation.

## Required factual validation

- [ ] Obtain the actual `cdr_dp_abai_default_20260903_17_00_00_p.csv` for the 2026-09-03 16:21–16:22 queue call.
- [ ] Match both captured `call_ref` values to CDR `CONN_ID` records and identify the operator record carrying the authoritative `T_ECD`.
- [ ] Only after that evidence, finalize external `Duration` / `finished` mapping.
- [ ] Later validate `lock_if_no_answer`, `lock_if_reject`, true two-free-agent multicall, external `NumberA`, and answered-agent `NumberB` with the required live facts.

## Rules

- No production ECSS changes from autonomous offline increments.
- Do not revisit confirmed licensing/VRRP/Mnesia/test-2000/agents/route-112 stages without new evidence.
- Never treat `T_DBA` as queue wait or infer a shared call identifier beyond what live evidence proves.
- Never bypass a red/stale Forgejo gate; local gate owns `main` merges.
