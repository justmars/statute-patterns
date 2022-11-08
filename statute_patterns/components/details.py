import datetime
from pathlib import Path

import yaml
from dateutil.parser import parse
from pydantic import BaseModel
from slugify import slugify

from .category import StatuteTitle
from .rule import Rule
from .utils import STATUTE_PATH, UNITS_MONEY, UNITS_NONE


class StatuteDetails(BaseModel):
    """Basic information loaded from files found in the proper path/s."""

    created: float
    modified: float
    title: str
    description: str
    id: str
    emails: list[str]
    date: datetime.date
    variant: int | None = 1
    titles: list[StatuteTitle] = []
    units: list[dict] = []

    @classmethod
    def set_units(cls, title: str, p: Path | None) -> list[dict]:
        if all([title and "appropriat" in title.lower()]):
            return UNITS_MONEY
        elif p and p.exists():
            return yaml.safe_load(p.read_bytes())
        return UNITS_NONE

    @classmethod
    def slug_id(cls, p: Path, dt: str, v: int | None):
        _temp = [p.parent.parent.stem, p.parent.stem, dt]
        if v:
            _temp.append(str(v))
        return slugify(" ".join(_temp))

    @classmethod
    def from_rule(cls, rule: Rule, base_path: Path = STATUTE_PATH):
        """From a constructed rule (see `Rule.from_path()`), get the details of said rule. Limitation: the category and identifier must be unique."""
        if not base_path.exists():
            raise Exception("Could not get proper path.")

        if not rule.serial_title:
            raise Exception("No serial title created.")

        _file = rule.get_first_path_to_details(STATUTE_PATH)
        if not _file:
            raise Exception("No path to details found.")

        d = yaml.safe_load(_file.read_bytes())
        dt, ofc_title, v = d.get("date"), d.get("law_title"), d.get("variant")
        if not all([ofc_title, dt]):
            raise Exception(f"Fail on: {dt=}, {ofc_title=}, {v=}")

        return cls(
            created=_file.stat().st_ctime,
            modified=_file.stat().st_mtime,
            id=(idx := cls.slug_id(_file, dt, v)),
            title=ofc_title,
            description=rule.serial_title,
            emails=d.get("emails", ["bot@lawsql.com"]),
            date=parse(d["date"]).date(),
            variant=v,
            units=cls.set_units(ofc_title, rule.units_path(_file.parent)),
            titles=list(
                StatuteTitle.generate(
                    **dict(
                        pk=idx,
                        official=ofc_title,
                        serial=rule.serial_title,
                        aliases=d.get("aliases"),
                    )
                )
            ),
        )
