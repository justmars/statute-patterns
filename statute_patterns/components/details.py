import datetime
from pathlib import Path

import yaml
from dateutil.parser import parse
from pydantic import BaseModel

from .category import StatuteSerialCategory, StatuteTitle
from .rule import Rule
from .short import get_short
from .utils import walk

STATUTE_DIR = Path().home().joinpath("code/corpus-statutes")


class StatuteDetails(BaseModel):
    """A instance is dependent on a statute path from a fixed
    `STATUTE_DIR`. The shape of the Python object will be different
    from the shape of the dumpable `.yml` export."""

    titles: list[StatuteTitle]
    rule: Rule
    variant: int
    date: datetime.date
    units: list[dict]

    def __repr__(self) -> str:
        return "/".join(
            [
                self.rule.cat.value,
                self.rule.id,
                self.date.isoformat(),
                f"{str(self.variant)}.yml",
            ]
        )

    @property
    def slug(self):
        return self.__repr__().removesuffix(".yml").replace("/", ".")

    def to_file(self):
        f = STATUTE_DIR.joinpath(self.__repr__())
        f.parent.mkdir(parents=True, exist_ok=True)
        data = self.model_dump()
        data["units"] = walk(data["units"])
        text = yaml.dump(data, width=60)
        return f.write_text(text)

    @classmethod
    def from_file(cls, file: Path):
        statute_path = file.parent.parent

        data = yaml.safe_load(file.read_bytes())
        official = data.get("title")
        if not official:
            return None

        category = StatuteSerialCategory.from_value(statute_path.parent.stem)
        if not category:
            return None

        serial = category.serialize(statute_path.stem)
        if not serial:
            return None

        return cls(
            rule=Rule(cat=category, id=statute_path.stem),
            variant=int(file.stem),
            date=parse(file.parent.stem).date(),
            units=data.get("units"),
            titles=list(
                StatuteTitle.generate(
                    official=official,
                    serial=serial,
                    short=data.get("short"),
                    aliases=data.get("aliases"),
                )
            ),
        )
