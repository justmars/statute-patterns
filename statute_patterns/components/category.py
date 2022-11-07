import re
from enum import Enum

from pydantic import BaseModel


class StatuteTitleCategory(str, Enum):
    """
    Each statute's title can be categorized as being the official title, a serialized title, an alias, and a short title.

    A `Rule` should contain at least 2 of these categories: (a) the official one which is the full length title; and (b) the serialized version which contemplates a category and an identifier.

    A statute however can also have a short title which is still official since it is made explicit by the rule itself.

    An alias on the other hand may not be an official way of referring to a statute but it is a popular way of doing so.
    """

    Official = "official"
    Serial = "serial"
    Alias = "alias"
    Short = "short"


class StatuteTitle(BaseModel):
    statute_id: str
    category: StatuteTitleCategory
    text: str

    class Config:
        use_enum_values = True


class StatuteSerialCategory(str, Enum):
    """
    This is a non-exhaustive taxonomy of Philippine legal rules for the purpose of enumerating fixed values.

    Both parts of the member declaration have meaning.

    The **name** of each statute category can be "uncamel"-ized to produce a serial title of the member for _most_ of the members enumerated.

    The **value** of each statute category serves 2 purposes:

    1. it refers to the folder to source raw .yaml files for the creation of the Statute object for the database; and
    2. it refers to the category as it appears in the database table.
    """

    RepublicAct = "ra"
    CommonwealthAct = "ca"
    Act = "act"
    Constitution = "const"
    Spain = "spain"
    BatasPambansa = "bp"
    PresidentialDecree = "pd"
    ExecutiveOrder = "eo"
    LetterOfInstruction = "loi"
    VetoMessage = "veto"
    RulesOfCourt = "roc"
    BarMatter = "rule_bm"
    AdministrativeMatter = "rule_am"
    ResolutionEnBanc = "rule_reso"
    CircularOCA = "oca_cir"
    CircularSC = "sc_cir"

    def serialize(self, idx: str):
        """Given a member item and a valid serialized identifier, create a serial title."""

        def uncamel(cat: StatuteSerialCategory):
            """See https://stackoverflow.com/a/9283563"""
            x = r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))"
            return re.sub(x, r" \1", cat.name)

        match self:
            case StatuteSerialCategory.Spain:
                if idx.lower() in ["civil", "penal"]:
                    return f"Spanish {idx.title()} Code"
                elif idx.lower() == "commerce":
                    return "Code of Commerce"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.Constitution:
                if idx.isdigit() and int(idx) in [1935, 1973, 1987]:
                    return f"{idx} Constitution"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.RulesOfCourt:
                if idx in ["1940", "1964", "responsibility_1988"]:
                    return f"{idx} Constitution"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.BatasPambansa:
                if idx.isdigit():
                    return f"{uncamel(self)} Blg. {idx}"
            case _:
                return f"{uncamel(self)} No. {idx}"
