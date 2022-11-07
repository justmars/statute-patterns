import pytest

from statute_patterns import Rule, StatuteCategory, count_rules, extract_rules
from statute_patterns.names import NamedRules
from statute_patterns.serials import SerializedRules


def path_to_rule(shared_datadir):
    civcode = Rule(
        statute_category=StatuteCategory.RepublicAct,
        statute_serial_id="386",
    )
    base = shared_datadir / "statutes"
    loc = civcode.get_path(base)
    assert loc and civcode.units_path(loc)
    assert isinstance(civcode.get_paths(base), list)
    assert isinstance(list(civcode.extract_folders(base)), list)
    assert civcode.units_path(base)


@pytest.mark.parametrize(
    "text, extracted, counted",
    [
        (
            "The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386",
            [
                {"statute_category": "ra", "statute_serial_id": "386"},
                {"statute_category": "ra", "statute_serial_id": "386"},
                {"statute_category": "spain", "statute_serial_id": "civil"},
            ],
            [
                {
                    "statute_category": "ra",
                    "statute_serial_id": "386",
                    "mentions": 2,
                },
                {
                    "statute_category": "spain",
                    "statute_serial_id": "civil",
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
                {"statute_category": "const", "statute_serial_id": "1987"},
                {"statute_category": "spain", "statute_serial_id": "penal"},
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
                    "statute_category": "rule_am",
                    "statute_serial_id": "02-11-10-sc",
                },
                {
                    "statute_category": "rule_am",
                    "statute_serial_id": "99-10-05-0",
                },
                {"statute_category": "ra", "statute_serial_id": "965"},
                {"statute_category": "ra", "statute_serial_id": "2630"},
                {"statute_category": "ca", "statute_serial_id": "613"},
            ],
        ),
        (
            "There is no question that Section 2 of Presidential Decree No. 1474-B is inconsistent with Section 62 of Republic Act No. 3844.; Petitioner’s case was decided under P.D. No. 971, as amended by P.D. No. 1707.",
            [
                {"statute_category": "pd", "statute_serial_id": "1474-b"},
                {"statute_category": "ra", "statute_serial_id": "3844"},
                {"statute_category": "pd", "statute_serial_id": "971"},
                {"statute_category": "pd", "statute_serial_id": "1707"},
            ],
        ),
    ],
)
def test_rule_find_all(text, result):
    assert (
        list(i.dict() for i in SerializedRules.extract_rules(text)) == result
    )
