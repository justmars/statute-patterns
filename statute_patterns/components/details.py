import datetime
from pathlib import Path

import yaml
from dateutil.parser import parse
from pydantic import BaseModel, EmailStr
from slugify import slugify

from .category import StatuteTitle
from .rule import Rule
from .short import get_short
from .utils import DETAILS_FILE, STATUTE_PATH, set_units


class StatuteDetails(BaseModel):
    """
    A `StatuteDetails` object presupposes the existence of a [`Rule`][rule-model]
    object.

    After all, it's only when there's a valid path to a [`Rule`][rule-model] that the
    details and provisions of that rule can be extracted. Some notable fields
    are described below:

    Field | Type | Function
    :--:|:--:|:--:
    rule | [`Rule`][rule-model] | How we source the path
    title | str | The statute's serial title, e.g. Republic Act No. 386
    description | str | The statute's official title, e.g. An Act to...
    """

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
    def slug_id(cls, p: Path, dt: str, v: int | None):
        """Use the path's parameters with the date and variant, to
        create a slug that can serve as the url / primary key of the
        statute."""
        _temp = [p.parent.parent.stem, p.parent.stem, dt]
        if v:
            _temp.append(str(v))
        return slugify(" ".join(_temp))

    @classmethod
    def from_rule(cls, rule: Rule, base_path: Path = STATUTE_PATH):
        """From a constructed rule (see [`Rule.from_path`][statute_patterns.components.rule.Rule.from_path]), get the
        details of said rule.  Limitation: the category and identifier must
        be unique."""  # noqa: E501
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
        units = set_units(ofc_title, rule.units_path(_file.parent))
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
            title=rule.serial_title,
            description=ofc_title,
            emails=d.get("emails", ["bot@lawsql.com"]),  # default to generic
            date=parse(d["date"]).date(),
            variant=v or 1,  # default to 1
            units=units,
            titles=list(titles),
        )
