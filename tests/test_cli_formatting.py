from check_username import format_datetime


def test_format_datetime_keeps_utc_time():
    value = "2006-10-09T18:21:32+00:00"

    result = format_datetime(value)

    assert result == "2006-10-09 18:21:32 UTC"


def test_format_datetime_converts_offset_to_utc():
    value = "2022-11-06T07:18:11+01:00"

    result = format_datetime(value)

    assert result == "2022-11-06 06:18:11 UTC"
