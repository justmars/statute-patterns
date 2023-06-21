import abc
import re
from collections.abc import Iterator
from re import Pattern

from pydantic import BaseModel, ConfigDict, Field, constr, field_validator

from .category import StatuteSerialCategory


class Rule(BaseModel):
    """A `Rule` is detected if it matches either:

    1. [`Named Patterns`][named-pattern] or
    2. [`Serial Patterns`][serial-pattern]

    Each rule implies:

    1. Previous validation via regex strings
    2. Serial title generated by [`StatuteSerialCategory.serialize()`][statute_patterns.components.category.StatuteSerialCategory.serialize]
    """  # noqa: E501

    model_config = ConfigDict(use_enum_values=True)
    cat: StatuteSerialCategory = Field(
        ...,
        title="Statute Category",
        description="Classification under the limited StatuteSerialCategory taxonomy.",
    )
    id: constr(to_lower=True) = Field(  # type: ignore
        ...,
        title="Serial Identifier",
        description=(
            "Limited inclusion of identifiers, e.g. only a subset of Executive"
            " Orders, Letters of Instruction, Spanish Codes will be permitted."
        ),
    )

    def __str__(self) -> str:
        return self.cat.serialize(self.id) or f"{self.cat.value=} {self.id=}"

    def __hash__(self):
        """Pydantic models are [not hashable by default](https://github.com/pydantic/pydantic/issues/1303#issuecomment-599712964).
        It is implemented here to take advantage of `collections.Counter` which works only on objects with a __hash__. This is the
        basis of [`count_rules()`][count-rules]."""  # noqa: E501
        return hash((type(self),) + tuple(self.__dict__.values()))

    @field_validator("cat", mode="before")
    def category_in_lower_case(cls, v):
        return StatuteSerialCategory(v.lower())

    @field_validator("id", mode="before")
    def serial_id_lower(cls, v):
        return v.lower()

    @property
    def serial_title(self):
        return StatuteSerialCategory(self.cat.value).serialize(self.id)


class BasePattern(BaseModel, abc.ABC):
    model_config = ConfigDict(use_enum_values=True)
    matches: list[str] = Field(
        default_factory=list,
        description="Text included _should_ match regex property.",
    )
    excludes: list[str] = Field(
        default_factory=list,
        description="Text included _should not_ match regex property.",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_matches()
        self.validate_excludes()

    @property
    @abc.abstractmethod
    def regex(self) -> str:
        """Includes `@group_name` in constructed regex `r'`string."""
        raise NotImplementedError(
            "Base regex to be later combined with other rules regex strings."
        )

    @property
    @abc.abstractmethod
    def group_name(self) -> str:
        """Used in @regex to identify `match.lastgroup`"""
        raise NotImplementedError("Used to identify `regex` capture group.")

    @property
    def pattern(self) -> Pattern:
        """Unique Pattern object per rule pattern created,
        regardless of it being a SerialPattern or a NamedPattern."""
        return re.compile(self.regex, re.X)

    def validate_matches(self) -> None:
        for sample in self.matches:
            if not self.pattern.fullmatch(sample):
                raise ValueError(f"Intended to be included but missing match: {sample}")

    def validate_excludes(self) -> None:
        for sample in self.excludes:
            if self.pattern.fullmatch(sample):
                raise ValueError(f"Intended to be excluded but match made: {sample}.")


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
