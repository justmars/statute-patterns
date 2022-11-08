import os
import re
from pathlib import Path
from typing import Iterator, Pattern

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


STATUTE_PATH = (
    Path().home().joinpath(os.getenv("STATUTE_PATH", "code/corpus/statutes"))
)

DETAILS_FILE = "details.yaml"

UNITS_MONEY = [
    {
        "item": "Container 1",
        "content": "Appropriation laws are excluded.",
    }
]
UNITS_NONE = [
    {
        "item": "Container 1",
        "content": "Individual provisions not detected.",
    }
]


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
