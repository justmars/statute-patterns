from pathlib import Path

import pytest

from statute_patterns import (
    Rule,
    StatuteDetails,
    StatuteSerialCategory,
    count_rules,
    extract_rules,
)
from statute_patterns.components import StatuteTitle
from statute_patterns.names import NamedRules
from statute_patterns.serials import SerializedRules


@pytest.fixture
def rule_obj():
    return Rule(cat=StatuteSerialCategory.RepublicAct, id="386")


@pytest.fixture
def base_folder(shared_datadir):
    return shared_datadir / "statutes"


@pytest.fixture
def statute_details(rule_obj: Rule, base_folder: Path):
    return StatuteDetails.from_rule(rule_obj, base_folder)


def test_category_serializer(rule_obj):
    assert rule_obj.serial_title == "Republic Act No. 386"


def test_paths_related_to_rule(rule_obj, base_folder):
    assert isinstance(rule_obj.get_paths(base_folder), list)
    assert isinstance(list(rule_obj.extract_folders(base_folder)), list)
    assert rule_obj.units_path(base_folder / rule_obj.cat / rule_obj.id)


def test_loaded_data(statute_details):
    assert isinstance(statute_details, StatuteDetails)
    assert isinstance(statute_details.titles, list)
    assert isinstance(statute_details.titles[0], StatuteTitle)


@pytest.mark.parametrize(
    "text, extracted, counted",
    [
        (
            "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386",
            [
                {"cat": "ra", "id": "386"},
                {"cat": "ra", "id": "386"},
                {"cat": "spain", "id": "civil"},
            ],
            [
                {
                    "cat": "ra",
                    "id": "386",
                    "mentions": 2,
                },
                {
                    "cat": "spain",
                    "id": "civil",
                    "mentions": 1,
                },
            ],
        ),
    ],
)
def test_extract_rules(text, extracted, counted):
    assert list(i.dict() for i in extract_rules(text)) == extracted
    assert list(count_rules(text)) == counted


@pytest.mark.parametrize(
    "text, result",
    [
        (
            "This is the 1987 PHIL CONST; hello world, the Spanish Penal Code.",
            [
                {"cat": "const", "id": "1987"},
                {"cat": "spain", "id": "penal"},
            ],
        ),
    ],
)
def test_extract_rules_named(text, result):
    assert list(i.dict() for i in NamedRules.extract_rules(text)) == result


@pytest.mark.parametrize(
    "text, result",
    [
        (
            "A.M. No. 02-11-10-SC or the Rules on Declaration of Absolute; Administrative Order No. 3 by enacting A.M. No. 99-10-05-0; Parenthetically, under these statutes [referring to RA Nos. 965 and 2630], Commonwealth Act (C.A.) No. 613, otherwise known as the <em>Philippine Immigration Act of 1940</em>",
            [
                {
                    "cat": "rule_am",
                    "id": "02-11-10-sc",
                },
                {
                    "cat": "rule_am",
                    "id": "99-10-05-0",
                },
                {"cat": "ra", "id": "965"},
                {"cat": "ra", "id": "2630"},
                {"cat": "ca", "id": "613"},
            ],
        ),
        (
            "There is no question that Section 2 of Presidential Decree No. 1474-B is inconsistent with Section 62 of Republic Act No. 3844.; Petitioner’s case was decided under P.D. No. 971, as amended by P.D. No. 1707.",
            [
                {"cat": "pd", "id": "1474-b"},
                {"cat": "ra", "id": "3844"},
                {"cat": "pd", "id": "971"},
                {"cat": "pd", "id": "1707"},
            ],
        ),
    ],
)
def test_rule_find_all(text, result):
    assert (
        list(i.dict() for i in SerializedRules.extract_rules(text)) == result
    )
