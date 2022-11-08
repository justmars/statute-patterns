from pathlib import Path

import pytest

from statute_patterns import Rule, StatuteDetails


@pytest.fixture
def base_folder(shared_datadir) -> Path:
    return shared_datadir / "statutes"


@pytest.fixture
def rule_obj(base_folder):
    return Rule.from_path(base_folder / "ra" / "386" / "details.yaml")


@pytest.fixture
def statute_details(rule_obj: Rule, base_folder: Path):
    return StatuteDetails.from_rule(rule_obj, base_folder)
