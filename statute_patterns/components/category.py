import re
from enum import Enum

from pydantic import BaseModel


class StatuteSerialCategory(str, Enum):
    """
    ## Concept
    It would be difficult to identify rules if they were arbitrarily named
    without a fixed point of reference. For instance the "Civil Code of the
    Philippines",  an arbitrary collection of letters, would be hard to find
    if laws were organized alphabetically.

    Fortunately, each Philippine `serial`-title rule belongs to an
    assignable `StatuteSerialCategory`. This is not an official reference but
    rather a non-exhaustive taxonomy of Philippine legal rules mapped to
    a `enum.Enum` object.

    Enum | Purpose
    --:|:--
    `name` | for _most_ members, can "uncamel"-ized to produce serial title
    `value` | (a) folder for discovering path / (b) category usable in the database table

    Using this model simplifies the ability to navigate rules. Going back to
    the Civil Code described above, its `serial` title is _Republic Act No. 386_ and
    thus can be mapped to the following folder: `/statutes/ra/386`. We can definitely
    categorize this as an _ra_ with a serial id of _386_.

    Mapped to its `Rule`, counterpart we get:

    Field | Value | Description
    :--:|:--:|:--
    `cat`| ra | Serial statute category
    `id` | 386 | Serial identifier of the category

    ## Purpose

    Knowing the path to a rule, we can later extract the rule's contents. (Note however that there can be more than one path since in exceptional cases, the combination of *category* + *serial id* does not yield a unique rule.)

    Examples:
        >>> StatuteSerialCategory
        <enum 'StatuteSerialCategory'>
        >>> StatuteSerialCategory._member_map_
        {'RepublicAct': <StatuteSerialCategory.RepublicAct: 'ra'>, 'CommonwealthAct': <StatuteSerialCategory.CommonwealthAct: 'ca'>, 'Act': <StatuteSerialCategory.Act: 'act'>, 'Constitution': <StatuteSerialCategory.Constitution: 'const'>, 'Spain': <StatuteSerialCategory.Spain: 'spain'>, 'BatasPambansa': <StatuteSerialCategory.BatasPambansa: 'bp'>, 'PresidentialDecree': <StatuteSerialCategory.PresidentialDecree: 'pd'>, 'ExecutiveOrder': <StatuteSerialCategory.ExecutiveOrder: 'eo'>, 'LetterOfInstruction': <StatuteSerialCategory.LetterOfInstruction: 'loi'>, 'VetoMessage': <StatuteSerialCategory.VetoMessage: 'veto'>, 'RulesOfCourt': <StatuteSerialCategory.RulesOfCourt: 'roc'>, 'BarMatter': <StatuteSerialCategory.BarMatter: 'rule_bm'>, 'AdministrativeMatter': <StatuteSerialCategory.AdministrativeMatter: 'rule_am'>, 'ResolutionEnBanc': <StatuteSerialCategory.ResolutionEnBanc: 'rule_reso'>, 'CircularOCA': <StatuteSerialCategory.CircularOCA: 'oca_cir'>, 'CircularSC': <StatuteSerialCategory.CircularSC: 'sc_cir'>}
    """  # noqa: E501

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
        """Given a member item and a valid serialized identifier, create a serial title.

        Note that the identifier must be upper-cased to make this consistent with the textual convention, e.g.

        1. `pd` + `570-a` = `Presidential Decree No. 570-A`
        2. `rule_am` + `03-06-13-sc` = `Administrative Matter No. 03-06-13-SC`
        """

        def uncamel(cat: StatuteSerialCategory):
            """See https://stackoverflow.com/a/9283563"""
            x = r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))"
            return re.sub(x, r" \1", cat.name)

        match self:  # noqa: E999 TODO: fix
            case StatuteSerialCategory.Spain:
                small_idx = idx.lower()
                if small_idx in ["civil", "penal"]:
                    return f"Spanish {idx.title()} Code"
                elif small_idx == "commerce":
                    return "Code of Commerce"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.Constitution:
                if idx.isdigit() and int(idx) in [1935, 1973, 1987]:
                    return f"{idx} Constitution"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.RulesOfCourt:
                if idx in ["1940", "1964"]:
                    return f"{idx} Rules of Court"
                elif idx in ["cpr"]:
                    return "Code of Professional Responsibility"
                raise SyntaxWarning(f"{idx=} invalid serial of {self}")

            case StatuteSerialCategory.VetoMessage:
                """No need to specify No.; understood to mean a Republic Act"""
                return f"Veto Message - {idx}"

            case StatuteSerialCategory.ResolutionEnBanc:
                """The `idx` needs to be a specific itemized date."""
                return f"Resolution of the Court En Banc dated {idx}"

            case StatuteSerialCategory.CircularSC:
                return f"SC Circular No. {idx}"

            case StatuteSerialCategory.CircularOCA:
                return f"OCA Circular No. {idx}"

            case StatuteSerialCategory.AdministrativeMatter:
                """Handle special rule with variants: e.g.`rule_am 00-5-03-sc-1` and `rule_am 00-5-03-sc-2`"""
                am = uncamel(self)
                small_idx = idx.lower()
                if "sc" in small_idx:
                    if small_idx.endswith("sc"):
                        return f"{am} No. {small_idx.upper()}"
                    elif sans_var := re.search(r"^.*-sc(?=-\d+)", small_idx):
                        return f"{am} No. {sans_var.group().upper()}"
                return f"{am} No. {small_idx.upper()}"

            case StatuteSerialCategory.BatasPambansa:
                if idx.isdigit():
                    return f"{uncamel(self)} Blg. {idx}"  # there are no -A -B suffixes in BPs

            case _:
                # no need to uppercase pure digits
                target_digit = idx if idx.isdigit() else idx.upper()
                return f"{uncamel(self)} No. {target_digit}"


class StatuteTitleCategory(str, Enum):
    """
    Each statute's title can be referred to in various ways.

    Category | Mandatory | Nature | Description | Example
    --:|:--:|:--:|:--|:--
    `official` | yes | official | full length title | _AN ACT TO PROVIDE PROTECTION TO BUYERS OF REAL ESTATE ON INSTALLMENT PAYMENTS_
    `serial` | yes | official | a `StatuteSerialCategory` and a serial identifier. | _Republic Act No. 6552_
    `short`  | no | official | may be declared in body of statute | _Realty Installment Buyer Act_
    `alias`  | no | unofficial | popular, undocumented means of referring to a statute | _Maceda Law_
    """

    Official = "official"
    Serial = "serial"
    Alias = "alias"
    Short = "short"


class StatuteTitle(BaseModel):
    """Will be used to populate the database; assumes a fixed `statute_id`."""

    statute_id: str
    category: StatuteTitleCategory
    text: str

    class Config:
        use_enum_values = True

    @classmethod
    def generate(
        cls,
        pk: str,
        official: str | None = None,
        serial: str | None = None,
        short: str | None = None,
        aliases: list[str] | None = None,
    ):
        if aliases:
            for title in aliases:
                if title and title != "":
                    yield cls(
                        statute_id=pk,
                        category=StatuteTitleCategory.Alias,
                        text=title,
                    )
        if short:
            yield cls(
                statute_id=pk,
                category=StatuteTitleCategory.Short,
                text=short,
            )

        if serial:
            yield cls(
                statute_id=pk,
                category=StatuteTitleCategory.Serial,
                text=serial,
            )

        if official:
            yield cls(
                statute_id=pk,
                category=StatuteTitleCategory.Official,
                text=official,
            )
