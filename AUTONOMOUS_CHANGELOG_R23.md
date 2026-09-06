# Autonomous changelog — r23 surplus CDR field guard

- Hardened offline `load_cdr(...)` against malformed CSV rows that contain more fields than the header.
- Python `csv.DictReader` represents such surplus values under a `None` key; the previous normalization path could therefore raise an incidental attribute error while attempting `.strip()` on a list.
- The loader now fails closed with deterministic `ValueError: CDR row has more fields than the header` before any queue-call correlation is attempted.
- Added standard-library `unittest` regression coverage using a synthetic CDR row with one surplus field.
- No ECSS production configuration, route 112, agents, licensing, VRRP, Mnesia, phones or live CDR state was changed.
- This change does not infer queue membership, logical call identity, queue wait, operator identity, or `finished.Duration`; a real captured queue CDR remains required for final live mapping.
