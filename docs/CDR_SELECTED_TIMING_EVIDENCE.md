# Selected operator CDR timing evidence

Status: offline deterministic tooling candidate; no production ECSS changes.

This document defines the scope of the selected-operator timing helpers accumulated in the current autonomous CDR-correlation branch.

## Preconditions

The helpers operate only after another step has already selected an exact operator-side CDR record. They do not discover a logical call, choose a queue leg, infer a caller/operator relationship, or fabricate missing live evidence.

## Timing fields

For the selected record:

- `T_ECD` is treated as the existing CDR duration/talk-time evidence field already confirmed by real direct-call mapping in `PROJECT_STATE.md`.
- `T_DBA` is treated as the existing delay-to-answer evidence field already confirmed by real direct-call mapping.
- numeric `0` is a present value, not the same as a missing field;
- missing/absent values remain missing and must not be silently converted into queue-wait or call-duration conclusions.

The offline helpers can classify whether timing evidence is complete and can report which of `T_ECD` / `T_DBA` is absent. They remain presentation/correlation aids only.

## Explicit non-claims

Until the real CDR file for the confirmed 112 queue call is available, these helpers must not claim:

- how many CDR records one queue call creates;
- which queue-call CDR record is authoritative for `finished.Duration`;
- that `T_DBA` equals total queue wait in the routed 112 scenario;
- that `CONN_ID` alone identifies the whole logical queue call;
- a final `CallRecordUrl` mapping.

`PROJECT_STATE.md` remains the canonical source of truth. Confirmed licensing, VRRP, Mnesia, test 2000, agents and route 112 are not part of this offline increment and must not be repeated or modified.
