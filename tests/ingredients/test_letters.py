import re

import pytest

from statute_patterns import ltr


@pytest.mark.parametrize(
    "let1, let2, text, detected",
    [
        ("R", "A", "This is RA. 1241", "RA."),
        ("R", "A", "This is R A 1241", "R A"),
        ("A", "M", "A.M. 141", "A.M."),
    ],
)
def test_letters(let1, let2, text, detected):
    assert (m := re.search(ltr(let1, let2), text)) and m.group(0) == detected


@pytest.mark.parametrize(
    "let1, let2, text",
    [
        ("R", "A", "This isR.A. 1241"),
        ("A", "M", "A..M. 141"),
    ],
)
def test_letters_will_not_match(let1, let2, text):
    assert not re.search(ltr(let1, let2), text)
