# Autonomous changelog — r26 exact Decimal CDR timing precision

- Replaced binary-float parsing of offline `T_ECD` / `T_DBA` evidence with exact `decimal.Decimal` parsing.
- Large integral values such as `9007199254740993` are no longer rounded by IEEE-754 conversion before becoming evidence.
- Fractional, negative and non-finite timing values still fail closed; integral decimal/comma forms such as `12.0` / `12,0` remain accepted.
- Added standard-library regression tests for exact large integers, integral decimal forms and invalid/fractional/non-finite inputs.
- This changes offline CDR parsing only. It does not infer the live queue-call duration, operator identity, queue membership or logical call id, and it changes no ECSS production configuration.
- The real captured queue CDR remains required before finalizing production `Duration` / `finished` mapping.
