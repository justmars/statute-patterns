import pytest

from statute_patterns import (
    NamedRules,
    SerializedRules,
    StatuteDetails,
    StatuteTitle,
    count_rules,
    extract_rules,
)


def test_category_serializer(rule_obj):
    assert rule_obj.serial_title == "Republic Act No. 386"


def test_loaded_data(rule_obj, statute_details):
    assert statute_details.rule == rule_obj
    assert isinstance(statute_details, StatuteDetails)
    assert isinstance(statute_details.titles, list)
    assert isinstance(statute_details.titles[0], StatuteTitle)


@pytest.mark.parametrize(
    "text, extracted, counted",
    [
        (
            "Veto Message - 11534",
            [
                {"cat": "veto", "id": "11534"},
            ],
            [
                {
                    "cat": "veto",
                    "id": "11534",
                    "mentions": 1,
                }
            ],
        ),
        (
            "Republic Act No. 386, 1114, and 11000-",
            [
                {"cat": "ra", "id": "386"},
                {"cat": "ra", "id": "1114"},
                {"cat": "ra", "id": "11000"},
            ],
            [
                {
                    "cat": "ra",
                    "id": "386",
                    "mentions": 1,
                },
                {
                    "cat": "ra",
                    "id": "1114",
                    "mentions": 1,
                },
                {
                    "cat": "ra",
                    "id": "11000",
                    "mentions": 1,
                },
            ],
        ),
        (
            (  # noqa: E501
                "The Civil Code of the Philippines, the old Spanish Civil"
                " Code; Rep Act No. 386"
            ),
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
            (  # noqa: E501
                "A.M. No. 02-11-10-SC or the Rules on Declaration of Absolute;"
                " Administrative Order No. 3 by enacting A.M. No. 99-10-05-0;"
                " Parenthetically, under these statutes [referring to RA Nos."
                " 965 and 2630], Commonwealth Act (C.A.) No. 613, otherwise"
                " known as the <em>Philippine Immigration Act of 1940</em>"
            ),
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
            (  # noqa: E501
                "There is no question that Section 2 of Presidential Decree"
                " No. 1474 is inconsistent with Section 62 of Republic Act No."
                " 3844.; Petitioner’s case was decided under P.D. No. 971, as"
                " amended by P.D. No. 1707."
            ),
            [
                {"cat": "pd", "id": "1474"},
                {"cat": "ra", "id": "3844"},
                {"cat": "pd", "id": "971"},
                {"cat": "pd", "id": "1707"},
            ],
        ),
        (
            (  # noqa: E501
                "Nonetheless, the Court has acknowledged the practical value"
                " of the process of marking the confiscated contraband and"
                " considered it as an initial stage in the chain of custody -"
                " a process preliminary and preparatory to the physical"
                " inventory and photograph requirements in Section 21 of"
                " Republic Act No. 9165:"
            ),
            [{"cat": "ra", "id": "9165"}],
        ),
        (
            (  # noqa: E501
                "As amended by Republic Act No. 9337- An Act Amending Sections"
                " 27, 28, 34, 106, 107, 108, 109, 110, 111, 112, 113, 114,"
                " 116, 117, 119, 121, 148, 151, 236, 237 and 288 of the"
                " National Internal Revenue Code of 1997"
            ),
            [{"cat": "ra", "id": "9337"}],
        ),
    ],
)
def test_rule_find_all(text, result):
    assert list(i.dict() for i in SerializedRules.extract_rules(text)) == result
