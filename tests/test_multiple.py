from statute_patterns import DETAILS_FILE, Rule


def test_folders_from_rule(base_folder, rule_am_00503_sc):
    assert len(list(rule_am_00503_sc.extract_folders(base_folder))) == 2


def test_description_path(base_folder, rule_am_00503_sc):
    for a in rule_am_00503_sc.extract_folders(base_folder):
        # each of the rules will have different descriptions, same title
        if detail := Rule.get_details(a / DETAILS_FILE):
            assert detail.title == "Administrative Matter No. 00-5-03-SC"
            assert a.stem in detail.id
