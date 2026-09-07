# Autonomous Changelog R50

- Added `tools/cdr_evidence_html_report.py` for a standalone human-readable HTML report from a sanitized r46+ evidence bundle.
- Report shows evidence item/record counts, exact classifications, caller refs and raw T_ECD/T_DBA values; ambiguous values remain `n/a`.
- The page states the evidence-only semantic boundary and never labels raw timing as queue wait or final call duration.
- User-controlled labels/refs are HTML-escaped; schema/warning/cardinality mismatches fail closed.
- Added regression coverage for readable output, escaping and inconsistent evidence rejection.
- No production ECSS/112/agent/routing/licensing changes were made.
