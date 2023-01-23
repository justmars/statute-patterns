import re
from re import Pattern

RA_DIGITS = r"(?:(?:[1-2]\d{1,4})|(?:[1-9]\d{1,3})|(?:[1-9]))"
"""Criteria:
1. Numbers should not start with 0
2. Numbers should not exceed 5 digits
3. Although at time of writing max RA is 11xxx (5 digits), added allowance for this to start with 2xxxx (still 5 digits)
"""

CA_DIGITS = r"(?:(?:[1-7]\d{1,2})|(?:[1-9]\d)|(?:[1-9]))"
"""Criteria:
1. Numbers should not start with 0
2. Numbers should not exceed 3 digits
3. There are 733 Commonwealth Acts numbered sequentially
"""

ACT_DIGITS = r"(?:(?:[1-4]\d{1,3})|(?:[1-9]\d{1,2})|(?:[1-9]))"
"""Criteria:
1. Numbers should not start with 0
2. Numbers should not exceed 4 digits
3. There are 4275 Acts of Congress numbered sequentially
"""

BP_DIGITS = r"(?:(?:[1-8]\d{1,2})|(?:[1-9]\d)|(?:[1-9]))"
"""Criteria:
1. Numbers should not start with 0
2. Numbers should not exceed 3 digits
3. There are 889 Batas Pambansa
"""


pds_with_letters = "|".join(
    [
        "429-A",
        "86-A",
        "1661-A",
        "1110-A",
        "1688-A",
        "629-A",
        "667-A",
        "1-A",
        "12-B",
        "637-A",
        "1877-A",
        "111-A",
        "401-A",
        "299-A",
        "1003-A",
        "389-A",
        "411-A",
        "570-A",
        "1802-A",
        "630-A",
        "1168-A",
        "6-A",
        "804-A",
        "865-A",
        "1727-A",
        "1158-A",
        "629-B",
        "1878-A",
        "1667-A",
        "621-A",
        "1258-A",
        "1716-A",
        "1-B",
        "1046-A",
        "571-A",
        "16-A",
        "1737-A",
        "12-A",
        "1756-A",
        "1822-A",
        "1067-A",
        "1458-A",
        "1843-A",
        "1605-A",
        "1664-A",
        "426-A",
        "99-A",
        "1220-A",
        "902-A",
        "51-A",
        "228-A",
        "865-B",
        "576-A",
    ]
)

PD_DIGITS = r"(?:(?:[1-2]\d{1,3})|(?:[1-9]\d{1,2})|(?:[1-9]))"
"""Criteria:
1. Numbers should not start with 0
2. Numbers should not exceed 3 digits
3. There are 2036 Presidential Decrees
"""

PD_DIGITS_PLUS = rf"{pds_with_letters}|{PD_DIGITS}"


EXTENDERS = "|".join([",", r"\s+", r"(\sand\s)"])
SEPARATOR: Pattern = re.compile(EXTENDERS)


def digitize(allowed_digits: str) -> str:
    """Adds a comma and spaces after the digit mark; multiple patterns of the same are allowed culiminating in a final digit."""
    return rf"(?:{allowed_digits}({EXTENDERS})+)*(?:{allowed_digits})"


def split_digits(text: str):
    for a in SEPARATOR.split(text):
        if a and a.strip() and a != "and":  # removes None, ''
            yield a.strip()
