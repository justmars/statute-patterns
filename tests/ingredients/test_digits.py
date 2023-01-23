import re

import pytest

from statute_patterns.recipes import (
    ACT_DIGITS,
    BP_DIGITS,
    CA_DIGITS,
    PD_DIGITS,
    PD_DIGITS_PLUS,
    RA_DIGITS,
    digitize,
    split_digits,
)

allowed_ra = re.compile(digitize(RA_DIGITS), re.X)


@pytest.mark.parametrize(
    "max, regex_digits",
    [
        (11932, RA_DIGITS),
        (733, CA_DIGITS),
        (4275, ACT_DIGITS),
        (899, BP_DIGITS),
        (2036, PD_DIGITS),
    ],
)
def test_ra_digit_matches(max, regex_digits):
    p = re.compile(regex_digits, re.X)
    for i in range(1, max):
        assert p.fullmatch(str(i))


@pytest.mark.parametrize(
    "text",
    ["429-A", "2036", "1", "12-B"],
)
def test_pd_digit_plus(text):
    assert re.fullmatch(PD_DIGITS_PLUS, text)


@pytest.mark.parametrize(
    "text, detected, specific_digits",
    [
        (
            "Hello 123, 999, and 124-",
            "123, 999, and 124",
            ["123", "999", "124"],
        ),
        (
            "Hello this is a test 123, 999, 124",
            "123, 999, 124",
            ["123", "999", "124"],
        ),
        (
            "Hello X X X  123 and 124",
            "123 and 124",
            ["123", "124"],
        ),
        (
            "Hello YYY  123",
            "123",
            ["123"],
        ),
    ],
)
def test_digits_multiple_matches(text, detected, specific_digits):
    assert (m := allowed_ra.search(text)) and m.group(0) == detected
    assert list(split_digits(detected)) == specific_digits


@pytest.mark.parametrize(
    "text",
    [
        "Hello",
        "Only words found here",
        "Even letters A, B",
    ],
)
def test_digit_does_not_match(text):
    assert not allowed_ra.search(text)
