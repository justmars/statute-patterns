import re

import pytest

from statute_patterns import digit_splitter, set_digit, set_digits

digit_pattern = re.compile(set_digit(), re.X)
digit_many_pattern = re.compile(set_digits(), re.X)


@pytest.mark.parametrize(
    "text, detected",
    [
        ("Hello 123", "123"),
        ("This is 123-ABC", "123-A"),
        ("This is 123ABC is", "123A"),
        ("This is 124141414 is", "124141"),
    ],
)
def test_digit_matches(text, detected):
    assert (m := digit_pattern.search(text)) and m.group(0) == detected
    assert (m := digit_many_pattern.search(text)) and m.group(0) == detected


@pytest.mark.parametrize(
    "text, detected, split_digits",
    [
        (
            "Hello 123, 999, and 124",
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
def test_digits_multiple_matches(text, detected, split_digits):
    assert (m := digit_many_pattern.search(text)) and m.group(0) == detected
    assert list(digit_splitter(detected)) == split_digits


@pytest.mark.parametrize(
    "text",
    [
        "Hello",
        "Only words found here",
        "Even letters A, B",
    ],
)
def test_digit_does_not_match(text):
    assert not digit_pattern.search(text)
