import datetime
from pathlib import Path

import yaml
from dateutil.parser import parse
from pydantic import BaseModel, EmailStr
from slugify import slugify

from .category import StatuteTitle
from .rule import Rule
from .short import get_short
from .utils import DETAILS_FILE, STATUTE_PATH, UNITS_MONEY, UNITS_NONE


class StatuteDetails(BaseModel):
    """Based on a `Rule` object, obtain details loaded from files found in a Rule's proper path."""

    created: float
    modified: float
    rule: Rule
    title: str
    description: str
    id: str
    emails: list[EmailStr]
    date: datetime.date
    variant: int
    titles: list[StatuteTitle]
    units: list[dict]

    @classmethod
    def set_units(cls, title: str, p: Path | None) -> list[dict]:
        """Extract the raw units of the statute and apply a special rule on appropriation laws when they're found."""
        if all([title and "appropriat" in title.lower()]):
            return UNITS_MONEY
        elif p and p.exists():
            return yaml.safe_load(p.read_bytes())
        return UNITS_NONE

    @classmethod
    def slug_id(cls, p: Path, dt: str, v: int | None):
        """Use the path's parameters with the date and variant, to create a slug that can serve as the url / primary key of the statute."""
        _temp = [p.parent.parent.stem, p.parent.stem, dt]
        if v:
            _temp.append(str(v))
        return slugify(" ".join(_temp))

    @classmethod
    def from_rule(cls, rule: Rule, base_path: Path = STATUTE_PATH):
        """From a constructed rule (see `Rule.from_path()`), get the details of said rule. Limitation: the category and identifier must be unique."""
        if not base_path.exists():
            raise Exception(f"Could not get proper {base_path=}.")

        if not rule.serial_title:
            raise Exception("No serial title created.")

        _file = None
        if folder := rule.get_path(base_path):
            _file = folder / DETAILS_FILE

        if not _file or not _file.exists():
            raise Exception(f"No _file found from {folder=} {base_path=}.")

        d = yaml.safe_load(_file.read_bytes())
        dt, ofc_title, v = d.get("date"), d.get("law_title"), d.get("variant")
        if not all([ofc_title, dt]):
            raise Exception(f"Fail on: {dt=}, {ofc_title=}, {v=}")
        units = cls.set_units(ofc_title, rule.units_path(_file.parent))
        idx = cls.slug_id(_file, dt, v)
        titles = StatuteTitle.generate(
            pk=idx,
            official=ofc_title,
            serial=rule.serial_title,
            short=get_short(units),
            aliases=d.get("aliases"),
        )
        return cls(
            created=_file.stat().st_ctime,
            modified=_file.stat().st_mtime,
            rule=rule,
            id=idx,
            title=ofc_title,
            description=rule.serial_title,
            emails=d.get("emails", ["bot@lawsql.com"]),  # default to generic
            date=parse(d["date"]).date(),
            variant=v or 1,  # default to 1
            units=units,
            titles=list(titles),
        )
