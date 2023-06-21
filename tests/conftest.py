import pytest

from statute_patterns import Rule, StatuteSerialCategory


@pytest.fixture
def base_folder(shared_datadir):
    return shared_datadir / "statutes"


@pytest.fixture
def rule_am_00503_sc():
    return Rule(cat=StatuteSerialCategory("rule_am"), id="00-5-03-sc")
