import abc
import os
import re
from enum import Enum
from pathlib import Path
from typing import Iterator, Pattern

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, constr, validator

load_dotenv(find_dotenv())

STATUTE_PATH = (
    Path().home().joinpath(os.getenv("STATUTE_PATH", "corpus/code/statutes"))
)


class StatuteCategory(str, Enum):
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

    @classmethod
    def serialize(cls, cat: "StatuteCategory", idx: str):
        """Given a member item and a valid serialized identifier, create a serial title."""

        def uncamel(cat: StatuteCategory):
            """See https://stackoverflow.com/a/9283563"""
            x = r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))"
            return re.sub(x, r" \1", cat.name)

        match cat:
            case StatuteCategory.Spain:
                if idx.lower() in ["civil", "penal"]:
                    return f"Spanish {idx.title()} Code"
                elif idx.lower() == "commerce":
                    return "Code of Commerce"
                raise SyntaxWarning(f"{idx=} invalid serial of {cat}")

            case StatuteCategory.Constitution:
                if idx.isdigit() and int(idx) in [1935, 1973, 1987]:
                    return f"{idx} Constitution"
                raise SyntaxWarning(f"{idx=} invalid serial of {cat}")

            case StatuteCategory.RulesOfCourt:
                if idx in ["1940", "1964", "responsibility_1988"]:
                    return f"{idx} Constitution"
                raise SyntaxWarning(f"{idx=} invalid serial of {cat}")

            case StatuteCategory.BatasPambansa:
                if idx.isdigit():
                    return f"{uncamel(cat)} Blg. {idx}"
            case _:
                return f"{uncamel(cat)} No. {idx}"


class Rule(BaseModel):
    """Identifies a statute based on two fields: (1) category and (2) serial_id. It is created through the use of either a NamedPattern or a SerialPattern."""

    cat: StatuteCategory = Field(
        ...,
        title="Statute Category",
        description="Classification under the limited StatuteCategory taxonomy.",
    )
    id: constr(to_lower=True) = Field(  # type: ignore
        ...,
        title="Serial Identifier",
        description="Limited inclusion of identifiers, e.g. only a subset of Executive Orders, Letters of Instruction, Spanish Codes will be permitted.",
    )

    class Config:
        use_enum_values = True

    def __hash__(self):
        """Pydantic models are not hashable by default. The implementation in this case becomes useful for the built-in collections.Counter (used in statute_patterns.count_rules). See https://github.com/pydantic/pydantic/issues/1303#issuecomment-599712964."""
        return hash((type(self),) + tuple(self.__dict__.values()))

    @validator("cat", pre=True)
    def category_in_lower_case(cls, v):
        return StatuteCategory(v.lower())

    @validator("id", pre=True)
    def serial_id_lower(cls, v):
        return v.lower()

    @property
    def serial_title(self):
        return StatuteCategory.serialize(self.cat, self.id)

    def get_path(self, base_path: Path = STATUTE_PATH) -> Path | None:
        """For most cases, there only be one path to path/to/statutes/ra/386 where:

        1. path/to/statutes = base_path
        2. 'ra' is the category
        3. '386' is the id.
        """
        target = base_path / self.cat / self.id
        if target.exists():
            return target
        return None

    def get_paths(self, base_path: Path = STATUTE_PATH) -> list[Path]:
        """The serial id isn't enough since the variant of a `StatuteRow.id` includes a `-<digit>` where the digit is the variant."""
        targets = []
        target = base_path / self.cat
        paths = target.glob(f"{self.id}-*/details.yaml")
        for variant_path in paths:
            if variant_path.exists():
                targets.append(variant_path.parent)
        return targets

    def extract_folders(
        self, base_path: Path = STATUTE_PATH
    ) -> Iterator[Path]:
        """Using the `category` and `id` of the object, get the possible folder paths."""
        if folder := self.get_path(base_path):
            yield folder
        else:
            if folders := self.get_paths(base_path):
                yield from folders

    def units_path(self, folder: Path) -> Path | None:
        """There are two kinds of unit files: the preferred / customized
        variant and the one scraped (the default in the absence of a preferred
        variant)."""
        text = f"{self.cat}{self.id}.yaml"
        preferred = folder / text
        if preferred.exists():
            return preferred

        default = folder / "units.yaml"
        if default.exists():
            return default

        return None


class BasePattern(BaseModel, abc.ABC):
    matches: list[str] = Field(
        default_factory=list,
        description="When supplied, text included _should_ match regex property.",
    )
    excludes: list[str] = Field(
        default_factory=list,
        description="When supplied, text included _should not_ match regex property.",
    )

    class Config:
        use_enum_values = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_matches()
        self.validate_excludes()

    @property
    @abc.abstractmethod
    def regex(self) -> str:
        """Combines the group_name with the desired regex string."""
        raise NotImplementedError(
            "Will be combined with other rule-like regex strings."
        )

    @property
    @abc.abstractmethod
    def group_name(self) -> str:
        """Added to regex string to identify the `match.lastgroup`"""
        raise NotImplementedError("Used to identify `regex` capture group.")

    @property
    def pattern(self) -> Pattern:
        """Enables use of a unique Pattern object per rule pattern created, regardless of it being a SerialPattern or a NamedPattern."""
        return re.compile(self.regex, re.X)

    def validate_matches(self) -> None:
        for m in self.matches:
            if not self.pattern.fullmatch(m):
                raise SyntaxError(
                    f"Missing match but intended to be included: {m}"
                )

    def validate_excludes(self) -> None:
        for ex in self.excludes:
            if self.pattern.match(ex):
                raise SyntaxError(
                    f"Match found even if intended to be excluded: {ex}."
                )


class BaseCollection(BaseModel, abc.ABC):
    """Whether a collection of Named or Serial patterns are instantiated, a `combined_regex` property and a `pattern` propery will be automatically created based on the collection of objects declared on instantiation of the class."""

    collection: list = NotImplemented

    @abc.abstractmethod
    def extract_rules(self, text: str) -> Iterator[Rule]:
        raise NotImplementedError("Need ability to fetch Rule objects.")

    @property
    def combined_regex(self) -> str:
        """Combine the different items in the collection (having .regex attribute) to form a single regex string."""
        return "|".join([r.regex for r in self.collection])

    @property
    def pattern(self) -> Pattern:
        return re.compile(self.combined_regex, re.X)


def stx(regex_text: str):
    """Remove indention of raw regex strings. This makes regex more readable when using rich.Syntax(<target_regex_string>, "python")"""
    return rf"""
{regex_text}
"""


SEPARATOR: Pattern = re.compile("|".join([",", r"\s+", r"(\sand\s)"]))


def digit_splitter(text: str):
    for a in SEPARATOR.split(text):
        if a and a.strip() and a != "and":  # removes None, ''
            yield a.strip()


def ltr(*args) -> str:
    """
    Most statutes are referred to in the following way:
    RA 8424, P.D. 1606, EO. 1008, etc. with spatial errors like
    B.  P.   22; some statutes are acronyms: "C.P.R." (code of professional responsibility)
    """
    joined = r"\.?\s*".join(args)
    return rf"(?:\b{joined}\.?)"


def add_num(prefix: str) -> str:
    num = r"(\s+No\.?s?\.?)?"
    return rf"{prefix}{num}"


def add_blg(prefix: str) -> str:
    blg = r"(\s+Blg\.?)?"
    return rf"{prefix}{blg}"


def set_digit() -> str:
    return r"\d{1,6}(:?[-–]?[AB]?)?"


def set_digits() -> str:
    """Adds a comma and spaces after the digit mark; multiple patterns of the same are allowed culiminating in a final digit."""
    x = set_digit()
    return rf"(?:(?:{x}[,\s]+)*(?:and\s+)?{x})"


def get_regexes(regexes: list[str], negate: bool = False) -> Iterator[str]:
    for x in regexes:
        if negate:
            yield rf"""(?<!{x}\s)
                """
        else:
            yield x


def not_prefixed_by_any(regex: str, lookbehinds: list[str]) -> str:
    """Add a list of "negative lookbehinds" (of fixed character lengths) to a target `regex` string."""
    return rf"""{''.join(get_regexes(lookbehinds, negate=True))}({regex})
    """


NON_ACT_INDICATORS = [
    r"An",  # "An act to ..."
    r"AN",  # "AN ACT ..."
    r"Republic",  # "Republic Act"
    r"Rep",
    r"Rep\.",
    r"REPUBLIC",
    r"Commonwealth",
    r"COMMONWEALTH",
]
"""If the word act is preceded by these phrases, do not consider the same to be a legacy act of congress."""
limited_acts = not_prefixed_by_any(rf"{add_num(r'Acts?')}", NON_ACT_INDICATORS)
