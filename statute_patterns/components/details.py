import datetime
from pathlib import Path

import yaml
from dateutil.parser import parse
from pydantic import BaseModel
from slugify import slugify

from .category import StatuteTitle
from .rule import Rule
from .utils import STATUTE_PATH


def slugify_id(p: Path, date: str, v: int | None = None):
    id_temp = " ".join([p.parent.parent.stem, p.parent.stem, date])
    if v:
        id_temp += f" {str(v)}"
    return slugify(id_temp)


class StatuteDetails(BaseModel):
    """Basic information loaded from files found in the proper path/s."""

    created: float
    modified: float
    title: str
    description: str
    id: str
    emails: list[str]
    date: datetime.date
    variant: int
    units: list[dict] = []
    titles: list[StatuteTitle] = []

    @classmethod
    def create_details(
        cls,
        serial_title: str,
        details_file: Path,
        units_file: Path | None,
    ):
        units = [{"item": "Container 1", "content": "Undetected."}]
        d = yaml.safe_load(details_file.read_bytes())
        ofc_title = d.get("law_title")
        if ofc_title and "appropriat" in ofc_title.lower():
            signal = "Appropriation laws exincluded."
            units = [{"item": "Container 1", "content": signal}]
        elif ofc_title and units_file and units_file.exists():
            units = yaml.safe_load(units_file.read_bytes())
        if ofc_title and serial_title and (dt := d.get("date")):
            pk = slugify_id(details_file, dt, d.get("variant"))
            title_input = dict(
                pk=pk,
                official=ofc_title,
                serial=serial_title,
                aliases=d.get("aliases"),
            )
            return StatuteDetails(
                created=details_file.stat().st_ctime,
                modified=details_file.stat().st_mtime,
                id=pk,
                title=ofc_title,
                description=serial_title,
                emails=d.get("emails", ["bot@lawsql.com"]),
                date=parse(d["date"]).date(),
                variant=d.get("variant", 1),
                units=units or [],
                titles=list(StatuteTitle.generate(**title_input)),
            )

    @classmethod
    def from_rule(cls, rule: Rule, base_path: Path = STATUTE_PATH):
        """From a constructed rule (see `Rule.from_path()`), get the details of said rule. Limitation: the category and identifier must be unique."""
        if not base_path.exists():
            return None

        d = rule.get_first_path_to_details(STATUTE_PATH)
        if not d:
            return None

        ser = rule.serial_title
        if not ser:
            return None

        _file = rule.units_path(d.parent)
        try:
            return cls.create_details(ser, d, _file)
        except StopIteration:
            return None
