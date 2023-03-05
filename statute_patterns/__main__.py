from collections import Counter
from collections.abc import Iterator

from .components import Rule
from .names import NamedRules
from .serials import SerializedRules


def extract_rules(text: str) -> Iterator[Rule]:
    """If text contains [serialized][serial-pattern] (e.g. _Republic Act No. 386_)
    and [named][named-pattern] rules (_the Civil Code of the Philippines_),
    extract the [`Rules`][rule-model] into their canonical serial variants.

    Examples:
        >>> from statute_patterns import extract_rules
        >>> text = "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"
        >>> list(extract_rules(text)) # get all rules
        [
            Rule(cat='ra', id='386'),
            Rule(cat='ra', id='386'),
            Rule(cat='spain', id='civil')
        ]

    Args:
        text (str): Text to search for statute patterns.

    Yields:
        Iterator[Rule]: Serialized Rules and Named Rule patterns
    """  # noqa: E501
    yield from SerializedRules.extract_rules(text)
    yield from NamedRules.extract_rules(text)


def extract_rule(text: str) -> Rule | None:
    """Thin wrapper over [`extract_rules()`][extract-rules]. If text contains a
    matching [`Rule`][rule-model], get the first one found.

    Examples:
        >>> from statute_patterns import extract_rule
        >>> text = "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"
        >>> extract_rule(text)  # get the first matching rule
        Rule(cat='ra', id='386')

    Args:
        text (str): Text to search for statute patterns.

    Returns:
        Rule | None: The first Rule found, if it exists
    """  # noqa: E501
    try:
        return next(extract_rules(text))
    except StopIteration:
        return None


def count_rules(text: str) -> Iterator[dict]:
    """Based on results from [`extract_rules()`][extract-rules],
    get the count of each unique rule found.

    Examples:
        >>> from statute_patterns import count_rules
        >>> text = "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"
        >>> list(count_rules(text)): # get unique rules with counts
        [
            {'cat': 'ra', 'id': '386', 'mentions': 2},
            {'cat': 'spain', 'id': 'civil', 'mentions': 1}
        ]

    Args:
        text (str): Text to search for statute patterns.

    Returns:
        Iterator[dict]: Unique rules converted into dicts with their counts
    """  # noqa: E501
    for k, v in Counter(extract_rules(text)).items():
        yield k.dict() | {"mentions": v}
