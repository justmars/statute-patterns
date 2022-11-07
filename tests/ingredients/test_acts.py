import re

import pytest

from statute_patterns.resources import limited_acts

act = re.compile(limited_acts, re.X)


@pytest.mark.parametrize(
    "text",
    [
        ("An Act No. 14"),
        ("This Republic Act No. 3015"),
        ("This Rep Act No. 3015"),
        ("This Commonwealth Act No. 3015"),
        ("This COMMONWEALTH Act No. 3015"),
    ],
)
def test_limited_acts(text):
    assert not act.search(text)


@pytest.mark.parametrize(
    "text, detected",
    [
        ("This Act No. 3015", "Act No."),
        ("This Batas Act No. 3015", "Act No."),
        ("Act Nos. 124, 3015", "Act Nos."),
    ],
)
def test_allowed_acts(text, detected):
    assert (m := act.search(text)) and m.group(0) == detected
