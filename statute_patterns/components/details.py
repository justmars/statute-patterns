import datetime
from collections import OrderedDict
from pathlib import Path

import yaml
from dateutil.parser import parse
from pydantic import BaseModel, EmailStr
from slugify import slugify

from .category import StatuteTitle
from .rule import Rule
from .short import get_short
from .utils import DETAILS_FILE, STATUTE_PATH, set_units


class literal(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")


yaml.add_representer(literal, literal_presenter)


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode("tag:yaml.org,2002:map", value)


yaml.add_representer(dict, represent_ordereddict)


def walk(nodes: list[dict]):
    if isinstance(nodes, list):
        revised_nodes = []
        for node in nodes:
            data = []
            if node.get("item"):
                candidate = node["item"]
                if candidate := str(node["item"]).strip():
                    if candidate.isdigit():
                        candidate = int(candidate)
                data.append(("item", candidate))
            if node.get("caption"):
                data.append(("caption", node["caption"].strip()))
            if node.get("content"):
                formatted_content = literal(node["content"].strip())
                data.append(("content", formatted_content))
            if node.get("units", None):
                walked_units = walk(node["units"])
                data.append(("units", walked_units))
            revised_nodes.append(dict(data))
    return revised_nodes


EXPORT_DIR = Path().home().joinpath("code/corpus-statutes")


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

    def make_exportable_path(self):
        from statute_patterns import extract_rule

        if not (clean_rule := extract_rule(self.title)):
            print(f"Could not extract rule from {self.title=}")
            return None

        target = "/".join(
            [
                clean_rule.cat.value,
                clean_rule.id,
                self.date.isoformat(),
                f"{str(self.variant)}.yml",
            ]
        )

        return EXPORT_DIR.joinpath(target)

    def make_exportable_data(self):
        data = {"title": self.description.strip()}
        for t in self.titles:
            if t.category.value == "alias":
                if "aliases" not in data:
                    data["aliases"] = []
                data["aliases"].append(t.text.strip())
            elif t.category.value == "short":
                data["short"] = t.text.strip()
        return data | {"units": self.units}

    def export(self):
        f = self.make_exportable_path()
        if not f:
            print(f"Lacking exportable path {self.id=}")
            return
        if f.exists():
            return

        f.parent.mkdir(parents=True, exist_ok=True)

        data = self.make_exportable_data()
        if not data:
            return

        data["units"] = walk(data["units"])
        text = yaml.dump(data, width=60)
        return f.write_text(text)

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
