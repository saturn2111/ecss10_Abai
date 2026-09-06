# Autonomous development changelog — r24 offline CDR header shape guard

- Added standalone `validate_cdr_header(...)` for deterministic offline validation of CDR column-name shape before future loader integration.
- The guard accepts only exact list/tuple containers of exact strings, trims outer whitespace, and rejects empty headers, blank column names and any duplicate normalized column name.
- Added standard-library `unittest` coverage for normalized order, duplicate optional columns, blank/non-string names, arbitrary iterable rejection and empty headers.
- This increment does not change the existing CDR loader or duration-selection semantics yet; integration remains a separate gated step after r24 is GREEN.
- It does not infer queue wait, logical call identity, operator identity, or `finished.Duration` mapping.
- No ECSS production configuration or live 112 state was changed. A real captured queue CDR remains required for final live mapping.
