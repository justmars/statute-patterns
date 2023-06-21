import datetime
from pathlib import Path

import yaml
from dateutil.parser import parse
from pydantic import BaseModel

from .category import StatuteSerialCategory, StatuteTitle
from .rule import Rule
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

    def __str__(self) -> str:
        return f"{self.rule.__str__()}, {self.date.strftime('%b %d, %Y')}"

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
        """Assumes the following path routing structure: `cat` / `num` / `date` / `variant`.yml,
        e.g. `ra/386/1946-06-18/1.yml` where each file contains the following metadata, the
        mandatory ones being "title" and "units". See example:

        ```yaml
        title: An Act to Ordain and Institute the Civil Code of the Philippines
        aliases:
        - New Civil Code
        - Civil Code of 1950
        short: Civil Code of the Philippines
        units:
        - item: Container 1
          caption: Preliminary Title
          units:
            - item: Chapter 1
              caption: Effect and Application of Laws
              units:
                - item: Article 1
                  content: >-
                    This Act shall be known as the "Civil Code of the Philippines."
                    (n)
                - item: Article 2
                  content: >-
                    Laws shall take effect after fifteen days following the
                    completion of their publication either in the Official
                    Gazette or in a newspaper of general circulation in the
                    Philippines, unless it is otherwise provided. (1a)
        ```
        """  # noqa: E501
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
