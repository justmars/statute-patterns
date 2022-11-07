__version__ = "0.0.1"

from .__main__ import count_rules, extract_rule, extract_rules
from .names import NamedPattern, NamedPatternCollection, NamedRules
from .resources import (
    Rule,
    add_blg,
    add_num,
    digit_splitter,
    ltr,
    set_digit,
    set_digits,
)
from .serials import (
    SerializedRules,
    SerialPattern,
    SerialPatternCollection,
    StatuteCategory,
)
