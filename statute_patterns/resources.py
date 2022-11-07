import abc
import datetime
import os
import re
from enum import Enum
from pathlib import Path
from typing import Iterator, NamedTuple, Pattern

import yaml
from dateutil.parser import parse
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, constr, validator
from slugify import slugify

load_dotenv(find_dotenv())


class StatuteDetails(NamedTuple):
    """Basic information loaded from files found in the proper path/s."""

    created: float
    modified: float
    id: str
    emails: list[str]
    date: datetime.date
    variant: int
    serial_title: str
    official_title: str
    alias_titles: list[str] = []
    units: list[dict] = []


STATUTE_PATH = (
    Path().home().joinpath(os.getenv("STATUTE_PATH", "code/corpus/statutes"))
)


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

    @classmethod
    def partial_extract(cls, d: StatuteDetails) -> Iterator["StatuteTitle"]:
        alias = StatuteTitleCategory.Alias
        ofc = StatuteTitleCategory.Official
        serial = StatuteTitleCategory.Serial
        for title in d.alias_titles:
            if title and title != "":
                yield cls(statute_id=d.id, category=alias, text=title)
        yield cls(statute_id=d.id, category=ofc, text=d.official_title)
        yield cls(statute_id=d.id, category=serial, text=d.serial_title)


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


class Rule(BaseModel):
    """Created primarily via `NamedPatternCollection` or a `SerialPatternCollection`, a `Rule` has many use cases:

    1. Prior validation by `NamedPattern` or a `SerialPattern` regex strings with Pydantic validation.
    2. Ensure a consistent path to an intended local directory via a uniform `StatuteSerialCategory` folder (`cat`) and a target serialized statute (`id`).
    3. Extract the details and units files from the path designated.
    4. Generate a serial title based on the `StatuteSerialCategory.serialize()` function.
    5. Be an exceptional Pydantic BaseModel which is countable through the collection.Counter built-in.
    """

    cat: StatuteSerialCategory = Field(
        ...,
        title="Statute Category",
        description="Classification under the limited StatuteSerialCategory taxonomy.",
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
        return StatuteSerialCategory(v.lower())

    @validator("id", pre=True)
    def serial_id_lower(cls, v):
        return v.lower()

    @property
    def serial_title(self):
        return StatuteSerialCategory(self.cat).serialize(self.id)

    def get_details(self, base_path: Path = STATUTE_PATH):
        def slugify_id(p: Path, date: str, v: int | None = None):
            id_temp = " ".join([p.parent.parent.stem, p.parent.stem, date])
            if v:
                id_temp += f" {str(v)}"
            return slugify(id_temp)

        try:
            if not base_path.exists():
                return None
            units = [{"item": "Container 1", "content": "Undetected."}]
            folder = next(self.extract_folders(STATUTE_PATH))
            units_file = self.units_path(folder)
            details_file = folder / "details.yaml"
            if details_file.exists:
                d = yaml.safe_load(details_file.read_bytes())
                ofc_title = d.get("law_title")
                if ofc_title and "appropriat" in ofc_title.lower():
                    signal = "Appropriation laws exincluded."
                    units = [{"item": "Container 1", "content": signal}]
                elif ofc_title and units_file and units_file.exists():
                    units = yaml.safe_load(units_file.read_bytes())
                if ofc_title and self.serial_title and (dt := d.get("date")):
                    return StatuteDetails(
                        created=details_file.stat().st_ctime,
                        modified=details_file.stat().st_mtime,
                        id=slugify_id(details_file, dt, d.get("variant")),
                        emails=d.get("emails", ["bot@lawsql.com"]),
                        date=parse(d["date"]).date(),
                        variant=d.get("variant"),
                        serial_title=self.serial_title,
                        official_title=d.get("law_title"),
                        alias_titles=d.get("aliases"),
                        units=units or [],
                    )
        except StopIteration:
            return None

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
        """The serial id isn't enough in complex statutes.

        To simplify, imagine Statute A, B and C have the same category and identifier. But refer to different documents.

        Because of this dilemma, we introduce a digit in the creation of statute folders referring to more than one variant of the intended document.

        So in the case of `/statutes/rule_am/`, let's consider `00-5-03-sc`. This should be valid statute under `self.get_path()`.

        However, since there exists 2 variants, we need to rename the original folder to contemplate 2 distinct documents:

        1. statutes/rule_am/00-5-03-sc-1
        2. statutes/rule_am/00-5-03-sc-2

        Both folders will be retrieved using the plural form of the function `self.get_paths()`
        """
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

    def units_path(self, statute_folder: Path) -> Path | None:
        """There are two kinds of unit files: the preferred / customized
        variant and the one scraped (the default in the absence of a preferred
        variant)."""
        preferred = statute_folder / f"{self.cat}{self.id}.yaml"
        if preferred.exists():
            return preferred

        default = statute_folder / "units.yaml"
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
