from .models import SerialPattern, SerialPatternCollection
from .resources import (
    StatuteCategory,
    add_blg,
    add_num,
    limited_acts,
    ltr,
    set_digits,
)

"""MODERN"""
ra = SerialPattern(
    statute_category=StatuteCategory.RepublicAct,
    regex_bases=[
        add_num(ltr("R", "A")),
        add_num(rf"Rep(ublic|\.)?\s+Act(\s*\({ltr('R','A')}\))?"),
    ],
    regex_serials=[set_digits()],
)
veto = SerialPattern(
    statute_category=StatuteCategory.VetoMessage,
    regex_bases=[rf"Veto\sMessage\s-\s"],
    regex_serials=[
        r"\d{5,}"
    ],  # use of this format limited to Codification histories, see ra 8484 (tax code)
    matches=["Veto Message - 11534"],  # referring to RA 11534
    excludes=["Veto Message"],
)

"""LEGACY"""
ca = SerialPattern(
    statute_category=StatuteCategory.CommonwealthAct,
    regex_bases=[
        add_num(ltr("C", "A")),
        add_num(rf"Com(monwealth|\.)?\s+Act(\s*\({ltr('C','A')}\))?"),
    ],
    regex_serials=[r"\d{1,3}(?:-[AB])?"],
)
bp = SerialPattern(
    statute_category=StatuteCategory.BatasPambansa,
    regex_bases=[
        add_blg(ltr("B", "P")),
        add_blg(rf"Batas\s+Pambansa(\s*\({ltr('B','P')}\))?"),
    ],
    regex_serials=[r"\d{1,3}(?:-[AB])?"],
)
act = SerialPattern(
    statute_category=StatuteCategory.Act,
    regex_bases=[limited_acts],
    regex_serials=[r"\d{1,4}"],
)


"""SPECIAL EXECUTIVE"""
pd = SerialPattern(
    statute_category=StatuteCategory.PresidentialDecree,
    regex_bases=[
        add_num(ltr("P", "D")),
        add_num(rf"Pres(idential|\.)?\s+Dec(ree|\.)?(\s*\({ltr('P','D')}\))?"),
    ],
    regex_serials=[r"\d{1,4}(?:-[AB])?"],
)
eo = SerialPattern(
    statute_category=StatuteCategory.ExecutiveOrder,
    regex_bases=[
        add_num(ltr("E", "O")),
        add_num(rf"Exec(utive|\.)?\s+Order?(\s*\({ltr('E','O')}\))?"),
    ],
    regex_serials=[
        "(?:292|209|229|228|14|1008|648|129-a|226|227|91)",  # popular based on opinions
        "(?:214|59|191|272|187|62|33|111|47|233)",  # used in codifications
    ],
    matches=["E.O. 292", "EO 47"],  # only specific numbers included
    excludes=["EO 1"],  # too many EO 1s in different administrations
)
loi = SerialPattern(
    statute_category=StatuteCategory.LetterOfInstruction,
    regex_bases=[
        add_num(ltr("L", "O", "I")),
        add_num(rf"Letters?\s+of\s+Instruction"),
    ],
    regex_serials=[
        "(?:474|729|97|270|926|1295|19|174|273|767|1416|713|968)"  # popular based on opinions
    ],
    matches=[
        "LOI 474",
        "Letter of Instruction No. 1295",
    ],  # only specific numbers included
    excludes=["Letter of Instruction No. 1"],
)


"""SC RULES"""
rule_am = SerialPattern(
    statute_category=StatuteCategory.AdministrativeMatter,
    regex_bases=[
        add_num(ltr("A", "M")),
        add_num(r"Adm(in)?\.?\s+Matter"),
        add_num(r"Administrative\s+Matter"),
    ],
    regex_serials=[r"(?:\d{1,2}-){3}SC\b", r"99-10-05-0\b"],
    matches=["Admin Matter No. 99-10-05-0"],
    excludes=["A.M. 141241", "Administrative Matter No. 12-12-12"],
)
rule_bm = SerialPattern(
    statute_category=StatuteCategory.BarMatter,
    regex_bases=[
        add_num(ltr("B", "M")),
        add_num(r"Bar\s+Matter"),
    ],
    regex_serials=[
        "(?:803|1922|1645|850|287|1132|1755|1960|209|1153)",  # popular based on opinions
        "(?:411|356)",  # used in codifications
    ],
    matches=["Bar Matter No.803"],
    excludes=["A.M. 141241", "Administrative Matter No. 12-12-12"],
)
sc_cir = SerialPattern(
    statute_category=StatuteCategory.CircularSC,
    regex_bases=[
        add_num(r"SC\s+Circular"),  # used in codifications
    ],
    regex_serials=[r"19"],
    matches=["SC Circular No. 19"],
    excludes=["SC Circular No. 1"],
)
oca_cir = SerialPattern(
    statute_category=StatuteCategory.CircularOCA,
    regex_bases=[
        add_num(r"OCA\s+Circular"),  # used in codifications
    ],
    regex_serials=[r"39-02"],
    matches=["OCA Circular No. 39-02"],
    excludes=["SC Circular No. 39"],
)
rule_reso = SerialPattern(
    statute_category=StatuteCategory.ResolutionEnBanc,
    regex_bases=[
        r"Resolution\sof\sthe\sCourt\sEn\sBanc\sdated",  # used in codifications
    ],
    regex_serials=[r"10-15-1991"],
    matches=["Resolution of the Court En Banc dated 10-15-1991"],
)


SerializedRules = SerialPatternCollection(
    collection=[
        ra,
        ca,
        act,
        eo,
        pd,
        bp,
        loi,
        rule_am,
        rule_bm,
        sc_cir,
        oca_cir,
    ]
)
