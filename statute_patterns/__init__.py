__version__ = "0.2.2"

from .__main__ import count_rules, extract_rule, extract_rules
from .components import (
    DETAILS_FILE,
    Rule,
    StatuteDetails,
    StatuteSerialCategory,
    StatuteTitle,
    StatuteTitleCategory,
    add_blg,
    add_num,
    ltr,
)
from .names import NamedPattern, NamedPatternCollection, NamedRules
from .serials import SerializedRules, SerialPattern, SerialPatternCollection
