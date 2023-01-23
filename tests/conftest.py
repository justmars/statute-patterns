from pathlib import Path

import pytest

from statute_patterns import Rule, StatuteDetails, StatuteSerialCategory


@pytest.fixture
def base_folder(shared_datadir):
    return shared_datadir / "statutes"


@pytest.fixture
def rule_obj(shared_datadir):
    return Rule.from_path(
        shared_datadir / "statutes" / "ra" / "386" / "details.yaml"
    )


@pytest.fixture
def statute_details(rule_obj: Rule, shared_datadir):
    return StatuteDetails.from_rule(rule_obj, shared_datadir / "statutes")


@pytest.fixture
def rule_am_00503_sc():
    return Rule(cat=StatuteSerialCategory("rule_am"), id="00-5-03-sc")
