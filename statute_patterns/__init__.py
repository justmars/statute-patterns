__version__ = "0.0.1"

from .__main__ import count_rules, extract_rule, extract_rules, load_rule_data
from .names import NamedPattern, NamedPatternCollection, NamedRules
from .resources import (
    Rule,
    StatuteDetails,
    StatuteSerialCategory,
    StatuteTitleCategory,
    add_blg,
    add_num,
    digit_splitter,
    ltr,
    set_digit,
    set_digits,
)
from .serials import SerializedRules, SerialPattern, SerialPatternCollection
