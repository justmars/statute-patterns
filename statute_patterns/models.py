import re
from typing import Iterator, Pattern

from pydantic import Field
from slugify import slugify

from .resources import BaseCollection, BasePattern, Rule, StatuteCategory


class NamedPattern(BasePattern):
    """A`Rule` can be extracted from a `NamedPattern`"""

    name: str
    regex_base: str
    rule: Rule

    @property
    def regex(self) -> str:
        from .resources import stx

        return stx(rf"(?P<{self.group_name}>{self.regex_base})")

    @property
    def group_name(self) -> str:
        """Provides unique identifier for each name pattern; assumes only one named pattern per rule."""
        return slugify(
            " ".join(
                [
                    self.rule.statute_category,
                    self.rule.statute_serial_id,
                ]
            ),
            separator="_",
            lowercase=True,
        )


class NamedPatternCollection(BaseCollection):
    """
    Each named legal title, not falling under the SerialNames Patterns, will also have its own manually crafted regex string, e.g.:

    collection=[
            NamedPattern(
                name='Old Civil Code',
                regex_base='\n    (?:\n    \\[?Spanish\\]?|\n    Old\n)\n    \\s+\n    Civil\n    \\s+\n    Code\n    \n    (:?\n        \\s+of\\s+18\\d{2}\n    )?\n\n',
                rule=Rule(statute_category='spain', statute_serial_id='civil')
            ),
            NamedPattern(
                name='Old Commerce Code',
                regex_base='\n    (?:\n    \\[?Spanish\\]?|\n    Old\n)\n    \\s+\n    Code\n    \\s+\n    of\n    \\s+\n    Commerce\n    \n    (:?\n        \\s+of\\s+18\\d{2}\n    )?\n\n',
                rule=Rule(statute_category='spain', statute_serial_id='commerce')
            ),
            NamedPattern(
                name='Old Penal Code',
                regex_base='\n    (?:\n    \\[?Spanish\\]?|\n    Old\n)\n    \\s+\n    Penal\n    \\s+\n    Code\n    \n    (:?\n        \\s+of\\s+18\\d{2}\n    )?\n\n',
                rule=Rule(statute_category='spain', statute_serial_id='penal')
            ),
            ...
        ]
    """

    collection: list[NamedPattern]

    def extract_rules(self, text: str) -> Iterator[Rule]:
        for m in self.pattern.finditer(text):
            for named in self.collection:
                if m.lastgroup == named.group_name:
                    yield named.rule


class SerialPattern(BasePattern):
    """A`Rule` can be extracted from a `SerialPattern`

    Each serial pattern refers to a specific category, e.g. RA, CA, etc. matched with a serial number.

    Unfortunately, the manner that such category can be formatted is varied; thus requiring a combination of regex bases and a possible list of serial numbers.

    Since the serial number may consist of composite values, this needs to be processed separately as well.
    """

    statute_category: StatuteCategory = Field(
        ...,
        description="A type of rule from the taxonomy enumerated under StatuteCategory.",
    )
    regex_bases: list[str] = Field(
        ...,
        description="There are too many ways to express a category name. There is a need to generate various regex strings which, when combined with the serial, can qualify for a serial rule.",
    )
    regex_serials: list[str] = Field(
        ...,
        description="The possible values of serial numbers to be matched with the regex_bases.",
    )

    @property
    def lines(self) -> Iterator[str]:
        """Each regex string produced matches the serial rule. Note the line break needs to be retained so that when printing `@regex`, the result is organized."""
        for base in self.regex_bases:
            for idx in self.regex_serials:
                yield rf"""({base}\s*{idx})
                """

    @property
    def group_name(self) -> str:
        return rf"serial_{self.statute_category}"

    @property
    def regex(self) -> str:
        return rf"(?P<{self.group_name}>{r'|'.join(self.lines)})"

    @property
    def digits_in_match(self) -> Pattern:
        return re.compile(r"|".join(self.regex_serials))


class SerialPatternCollection(BaseCollection):
    """Each category-based, serial-numbered, legal title will have a regex string, e.g. Republic Act is a category, a serial number for this category is 386 representing the Philippine Legal Code.

     collection=[
                SerialPattern(
                    statute_category='ra',  # Republic Act and its variant styles
                    regex_bases=[
                        '(?:\\bR\\.?\\s*A\\.?)(\\s+No\\.?s?\\.?)?',
                        'Rep(ublic|\\.)?\\s+Act(\\s*\\((?:\\bR\\.?\\s*A\\.?)\\))?(\\s+No\\.?s?\\.?)?'
                    ],
                    regex_serials=[
                        '(?:(?:\\d{1,6}(:?[-–]?[AB]?)?[,\\s]+)*(?:and\\s+)?\\d{1,6}(:?[-–]?[AB]?)?)'
                    ]
                ),
        ... # more
    ]

    """

    collection: list[SerialPattern]

    def extract_rules(self, text: str) -> Iterator[Rule]:
        """Each `m`, a python Match object, represents a serial pattern category with possible ambiguous identifier found.

        So running `m.group(0)` should yield the entire text of the match which consists of (a) the definitive category; and (b) the ambiguous identifier.

        The identifier is ambiguous because it may be a compound one, e.g. 'Presidential Decree No. 1 and 2'. In this case, there should be 2 matches produced not just one.

        This function splits the identifier by commas `,` and the word `and` to get the individual component identifiers.
        """
        from .resources import digit_splitter

        for match in self.pattern.finditer(text):
            for sp in self.collection:
                if match.lastgroup == sp.group_name:
                    if candidates := sp.digits_in_match.search(match.group(0)):
                        for d in digit_splitter(candidates.group(0)):
                            c = sp.statute_category
                            yield Rule(statute_category=c, statute_serial_id=d)
