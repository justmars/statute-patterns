import pytest

from statute_patterns import StatuteSerialCategory


@pytest.mark.parametrize(
    "cat, id, serial",
    [
        (
            "veto",
            "11534",
            "Veto Message - 11534",
        ),  # note special rule on veto messages
        (
            "rule_reso",
            "10-15-1991",
            "Resolution of the Court En Banc dated 10-15-1991",
        ),  # note special rule on veto message
        (
            "sc_cir",
            "19",
            "SC Circular No. 19",
        ),  # note reverse Enum name
        (
            "oca_cir",
            "39-02",
            "OCA Circular No. 39-02",
        ),  # note reverse Enum name
        (
            "pd",
            "570-a",
            "Presidential Decree No. 570-A",
        ),  # note capitalized id
        (
            "rule_am",
            "03-06-13-sc",
            "Administrative Matter No. 03-06-13-SC",
        ),  # note capitalized id
        (
            "rule_am",
            "00-5-03-sc-1",
            "Administrative Matter No. 00-5-03-SC",
        ),  # note special rule on varianted rule_ams
        ("ra", "386", "Republic Act No. 386"),
    ],
)
def test_serializer(cat, id, serial):
    assert StatuteSerialCategory(cat).serialize(id) == serial
