# Autonomous Changelog — r51

- Confirmed the standalone r50 human-readable HTML report auto-merged into `main` as `849ff2d0aa46a9e0c3d8a9bd2c255e1bb9fae624`.
- Added local browser search across sanitized label/caller-ref/classification values, exact classification filter, Reset and visible result count.
- The generated report remains a single standalone HTML file and performs filtering without ECSS/network access.
- All dynamic row/filter values remain HTML-escaped. Raw `T_ECD/T_DBA` keep evidence-only labels and are not inferred as queue wait or final Duration.
- Added regression coverage for the filtering controls/predicates while retaining escaping/cardinality checks.
- No live ECSS, 112 route, agent, licensing, VRRP or Mnesia change was made. Final r51 SHA remains pending Forgejo.
