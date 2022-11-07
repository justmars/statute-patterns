from collections import Counter
from typing import Iterator

from .names import NamedRules
from .resources import Rule
from .serials import SerializedRules


def extract_rules(text: str) -> Iterator[Rule]:
    """If text contains matching serialized (e.g. Republic Act No. 386) and named rules ('the Civil Code of the Philippines'), produce both.

    >>> text = "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"
    >>> list(extract_rules(text)) # get all rules
    [
        Rule(statute_category='ra', statute_serial_id='386'),
        Rule(statute_category='ra', statute_serial_id='386'),
        Rule(statute_category='spain', statute_serial_id='civil')
    ]
    """
    yield from SerializedRules.extract_rules(text)
    yield from NamedRules.extract_rules(text)


def extract_rule(text: str) -> Rule | None:
    """If text contains a matching rule, get the first rule found.

    >>> text = "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"
    >>> extract_rule(text)  # get the first matching rule
    Rule(statute_category='ra', statute_serial_id='386')
    """
    try:
        return next(extract_rules(text))
    except StopIteration:
        return None


def count_rules(text: str) -> Iterator[dict]:
    """Based on results from `extract_rules(text)`, get the count of each unique rule found.

    >>> text = "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"
    >>> list(count_rules(text)): # get unique rules with counts
    [
        {'statute_category': 'ra', 'statute_serial_id': '386', 'mentions': 2},
        {'statute_category': 'spain', 'statute_serial_id': 'civil', 'mentions': 1}
    ]
    """
    for k, v in Counter(extract_rules(text)).items():
        yield k.dict() | {"mentions": v}
