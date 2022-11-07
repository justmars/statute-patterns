import datetime
from pathlib import Path
from typing import NamedTuple

import yaml
from dateutil.parser import parse
from slugify import slugify

from .category import StatuteTitle, StatuteTitleCategory


def slugify_id(p: Path, date: str, v: int | None = None):
    id_temp = " ".join([p.parent.parent.stem, p.parent.stem, date])
    if v:
        id_temp += f" {str(v)}"
    return slugify(id_temp)


def extract_titles(
    pk: str,
    official: str,
    serial: str | None,
    aliases: list[str] | None = None,
):
    if aliases:
        for title in aliases:
            if title and title != "":
                yield StatuteTitle(
                    statute_id=pk,
                    category=StatuteTitleCategory.Alias,
                    text=title,
                )
    if serial:
        yield StatuteTitle(
            statute_id=pk, category=StatuteTitleCategory.Serial, text=serial
        )
    yield StatuteTitle(
        statute_id=pk,
        category=StatuteTitleCategory.Official,
        text=official,
    )


class StatuteDetails(NamedTuple):
    """Basic information loaded from files found in the proper path/s."""

    created: float
    modified: float
    id: str
    emails: list[str]
    date: datetime.date
    variant: int
    units: list[dict] = []
    titles: list[StatuteTitle] = []

    @classmethod
    def create_details(
        cls,
        details_file: Path,
        units_file: Path | None,
        serial_title: str | None,
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
            id = slugify_id(details_file, dt, d.get("variant"))
            return StatuteDetails(
                created=details_file.stat().st_ctime,
                modified=details_file.stat().st_mtime,
                id=id,
                emails=d.get("emails", ["bot@lawsql.com"]),
                date=parse(d["date"]).date(),
                variant=d.get("variant"),
                units=units or [],
                titles=list(
                    extract_titles(
                        pk=id,
                        official=ofc_title,
                        serial=serial_title,
                        aliases=d.get("aliases"),
                    )
                ),
            )
