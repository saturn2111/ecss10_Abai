from __future__ import annotations

from datetime import datetime, timedelta


def expected_closed_cdr_filename(
    call_time: datetime,
    *,
    domain: str = "dp_abai",
    profile: str = "default",
) -> str:
    """Return the ECSS hourly closed-CSV filename expected to contain a call.

    ECSS names a closed hourly file with the *end* of the covered hour. For
    example a call at 16:21 belongs to the file stamped 17:00. This helper is
    offline-only and does not access or modify ECSS.
    """

    if type(call_time) is not datetime:
        raise TypeError("call_time must be an exact datetime")

    for name, value in (("domain", domain), ("profile", profile)):
        if type(value) is not str:
            raise TypeError(f"{name} must be an exact string")
        if not value or value != value.strip():
            raise ValueError(f"{name} must be non-blank and already trimmed")
        if any(ch in value for ch in "/\\\r\n\t"):
            raise ValueError(f"{name} contains an unsafe filename character")

    hour_start = call_time.replace(minute=0, second=0, microsecond=0)
    hour_end = hour_start + timedelta(hours=1)
    stamp = hour_end.strftime("%Y%m%d_%H_00_00")
    return f"cdr_{domain}_{profile}_{stamp}_p.csv"
