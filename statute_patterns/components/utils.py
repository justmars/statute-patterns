import os
from collections.abc import Iterator
from pathlib import Path

import yaml
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


def set_units(title: str, p: Path | None) -> list[dict]:
    """Extract the raw units of the statute and apply a special rule on appropriation laws when they're found."""
    if p:
        if p.exists():
            try:
                units_as_list = yaml.safe_load(p.read_bytes())
                if not isinstance(units_as_list, list):
                    return UNITS_NONE
                return units_as_list
            except Exception:
                return UNITS_NONE
    if all([title and "appropriat" in title.lower()]):
        return UNITS_MONEY
    return UNITS_NONE


def stx(regex_text: str):
    """Remove indention of raw regex strings. This makes regex more readable when using rich.Syntax(<target_regex_string>, "python")"""
    return rf"""
{regex_text}
"""


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
