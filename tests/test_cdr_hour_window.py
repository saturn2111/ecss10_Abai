from datetime import datetime

import pytest

from tools.cdr_hour_window import expected_closed_cdr_filename


def test_call_in_16_hour_maps_to_17_closed_file():
    assert expected_closed_cdr_filename(datetime(2026, 9, 3, 16, 21, 59)) == (
        "cdr_dp_abai_default_20260903_17_00_00_p.csv"
    )


def test_hour_window_rolls_over_midnight():
    assert expected_closed_cdr_filename(datetime(2026, 9, 3, 23, 59, 59)) == (
        "cdr_dp_abai_default_20260904_00_00_00_p.csv"
    )


def test_custom_domain_and_profile_are_deterministic():
    assert expected_closed_cdr_filename(
        datetime(2026, 9, 3, 8, 0), domain="lab", profile="audit"
    ) == "cdr_lab_audit_20260903_09_00_00_p.csv"


@pytest.mark.parametrize("call_time", [None, "2026-09-03T16:21:00", 0])
def test_non_datetime_fails_closed(call_time):
    with pytest.raises(TypeError):
        expected_closed_cdr_filename(call_time)


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"domain": " dp_abai"}, ValueError),
        ({"profile": ""}, ValueError),
        ({"domain": "bad/name"}, ValueError),
        ({"profile": 7}, TypeError),
    ],
)
def test_filename_components_fail_closed(kwargs, error):
    with pytest.raises(error):
        expected_closed_cdr_filename(datetime(2026, 9, 3, 16, 21), **kwargs)
