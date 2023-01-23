import abc
import re
from collections.abc import Iterator
from pathlib import Path
from re import Pattern

from pydantic import BaseModel, Field, constr, validator

from .category import StatuteSerialCategory
from .utils import DETAILS_FILE, STATUTE_PATH


class Rule(BaseModel):
    """Created primarily via `NamedPatternCollection` or
    a `SerialPatternCollection`, a `Rule` has many use cases:

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

    @classmethod
    def get_details(cls, details_path: Path):
        """Assumes a properly structured path with three path
        parents from details.yaml, e.g. path to `/statutes/ra/386/details.yaml`
        means 3 parents from the same would be /statutes. Will
        create the rule based on the details path and pull data from other
        related paths to generate the details of the rule."""
        from .details import StatuteDetails

        if rule := cls.from_path(details_path):
            statute_path = details_path.parent.parent.parent
            return StatuteDetails.from_rule(rule, statute_path)
        return None

    @classmethod
    def from_path(cls, details_path: Path):
        """Construct rule from a properly structured statute's `details.yaml` file."""
        dir = details_path.parent
        cat = dir.parent.stem
        idx = dir.stem
        if details_path.name == DETAILS_FILE:
            return cls(cat=StatuteSerialCategory(cat), id=idx)
        return None

    @property
    def serial_title(self):
        return StatuteSerialCategory(self.cat).serialize(self.id)

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

        To simplify, imagine Statute A, B and C have the same
        category and identifier. But refer to different documents.

        Because of this dilemma, we introduce a digit in the creation of statute
        folders referring to more than one variant of the intended document.

        So in the case of `/statutes/rule_am/`, let's consider `00-5-03-sc`.
        This should be valid statute under `self.get_path()`.

        However, since there exists 2 variants, we need to rename the original
        folder to contemplate 2 distinct documents:

        1. statutes/rule_am/00-5-03-sc-1
        2. statutes/rule_am/00-5-03-sc-2

        Both folders will be retrieved using the plural form of
        the function `self.get_paths()`
        """
        targets = []
        target = base_path / self.cat
        paths = target.glob(f"{self.id}-*/{DETAILS_FILE}")
        for variant_path in paths:
            if variant_path.exists():
                targets.append(variant_path.parent)
        return targets

    def extract_folders(
        self, base_path: Path = STATUTE_PATH
    ) -> Iterator[Path]:
        """Using the `category` and `id` of the object,
        get the possible folder paths."""
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
            "Base regex to be later combined with other rules regex strings."
        )

    @property
    @abc.abstractmethod
    def group_name(self) -> str:
        """Added to regex string to identify the `match.lastgroup`"""
        raise NotImplementedError("Used to identify `regex` capture group.")

    @property
    def pattern(self) -> Pattern:
        """Enables use of a unique Pattern object per rule pattern created,
        regardless of it being a SerialPattern or a NamedPattern."""
        return re.compile(self.regex, re.X)

    def validate_matches(self) -> None:
        for example_text in self.matches:
            if not self.pattern.fullmatch(example_text):
                raise ValueError(
                    f"Missing match but intended to be included: {example_text}"
                )

    def validate_excludes(self) -> None:
        for example_text in self.excludes:
            if self.pattern.fullmatch(example_text):
                raise ValueError(
                    f"Match found even if intended to be excluded: {example_text}."
                )


class BaseCollection(BaseModel, abc.ABC):
    """Whether a collection of Named or Serial patterns are instantiated,
    a `combined_regex` property and a `pattern` propery will be automatically
    created based on the collection of objects declared on instantiation
    of the class."""

    collection: list = NotImplemented

    @abc.abstractmethod
    def extract_rules(self, text: str) -> Iterator[Rule]:
        raise NotImplementedError("Need ability to fetch Rule objects.")

    @property
    def combined_regex(self) -> str:
        """Combine the different items in the collection
        (having .regex attribute) to form a single regex string."""
        return "|".join([r.regex for r in self.collection])

    @property
    def pattern(self) -> Pattern:
        return re.compile(self.combined_regex, re.X)
