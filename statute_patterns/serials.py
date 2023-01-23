from .components import (
    StatuteSerialCategory,
    add_blg,
    add_num,
    limited_acts,
    ltr,
)
from .models import SerialPattern, SerialPatternCollection
from .recipes import (
    ACT_DIGITS,
    BP_DIGITS,
    CA_DIGITS,
    PD_DIGITS_PLUS,
    RA_DIGITS,
    digitize,
)

"""MODERN"""
ra = SerialPattern(
    cat=StatuteSerialCategory.RepublicAct,
    regex_bases=[
        add_num(ltr("R", "A")),
        add_num(rf"Rep(ublic|\.)?\s+Act(\s*\({ltr('R','A')}\))?"),
    ],
    regex_serials=[digitize(RA_DIGITS)],
    matches=[
        "Republic Act No. 7160",
        "Rep Act No. 386",
        "R.A. 386 and 7160",
        "Rep Act Nos. 124, 325",
        "Republic Act Nos. 124, 325, 1444, and 11111",
    ],
    excludes=["Republic Act No. 7160:", "RA 9337-"],
)
veto = SerialPattern(
    cat=StatuteSerialCategory.VetoMessage,
    regex_bases=[r"Veto\sMessage\s-\s"],
    regex_serials=[
        r"\d{4,7}"  # only Republic Acts will have vetos
    ],  # use of this format limited to Codification histories, see ra 8484 (tax code)
    matches=["Veto Message - 11534"],  # referring to RA 11534
    excludes=["Veto Message -", "Veto Message - 113"],
)

"""LEGACY"""
ca_digits = r""
ca = SerialPattern(
    cat=StatuteSerialCategory.CommonwealthAct,
    regex_bases=[
        add_num(ltr("C", "A")),
        add_num(rf"Com(monwealth|\.)?\s+Act(\s*\({ltr('C','A')}\))?"),
    ],
    regex_serials=[digitize(CA_DIGITS)],
    matches=[
        "Com. Act No. 23",
        "Commonwealth Act No. 733",
        "Com. Act Nos. 111, 700, and 733",
    ],
    excludes=[
        "C.A. 001",
        "CA No. 001",
        "Commonwealth Act No. 800",
    ],
)
bp = SerialPattern(
    cat=StatuteSerialCategory.BatasPambansa,
    regex_bases=[
        add_blg(ltr("B", "P")),
        add_blg(rf"Batas\s+Pambansa(\s*\({ltr('B','P')}\))?"),
    ],
    regex_serials=[digitize(BP_DIGITS)],
    matches=["B.P. 1"],
    excludes=["B.P. 900"],
)
act = SerialPattern(
    cat=StatuteSerialCategory.Act,
    regex_bases=[limited_acts],
    regex_serials=[digitize(ACT_DIGITS)],
    matches=["Act 1", "Act 10", "Act No. 250", "Act No. 4500"],
    excludes=["Act No. 5000", "Act 05"],
)


"""SPECIAL EXECUTIVE"""
pd = SerialPattern(
    cat=StatuteSerialCategory.PresidentialDecree,
    regex_bases=[
        add_num(ltr("P", "D")),
        add_num(rf"Pres(idential|\.)?\s+Dec(ree|\.)?(\s*\({ltr('P','D')}\))?"),
    ],
    regex_serials=[
        digitize(PD_DIGITS_PLUS)
    ],  # the acronyms must precede the regulars otherwise will match the regulars first
)
eo = SerialPattern(
    cat=StatuteSerialCategory.ExecutiveOrder,
    regex_bases=[
        add_num(ltr("E", "O")),
        add_num(rf"Exec(utive|\.)?\s+Order?(\s*\({ltr('E','O')}\))?"),
    ],
    regex_serials=[
        r"(?:129-A)",  # the acronyms must precede the regulars otherwise will match the regulars first
        r"(?:292|209|229|228|14|1008|648|226|227|91|179)",  # popular based on opinions
        r"(?:200|214|59|191|272|187|62|33|111|47|233|179|203|252)",  # used in codifications
    ],
    matches=[
        "E.O. 292",
        "EO 47",
        "Exec. Order No. 111",
    ],  # only specific numbers included
    excludes=["EO 1"],  # too many EO 1s in different administrations
)
loi = SerialPattern(
    cat=StatuteSerialCategory.LetterOfInstruction,
    regex_bases=[
        add_num(ltr("L", "O", "I")),
        add_num(r"Letters?\s+of\s+Instruction"),
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
    cat=StatuteSerialCategory.AdministrativeMatter,
    regex_bases=[
        add_num(ltr("A", "M")),
        add_num(r"Adm(in)?\.?\s+Matter"),
        add_num(r"Administrative\s+Matter"),
    ],
    regex_serials=[r"(?:\d{1,2}-){3}SC\b", r"99-10-05-0\b"],
    matches=["Admin Matter No. 99-10-05-0"],
    excludes=["A.M. 141241", "Administrative Matter No. 12-12-12"],
)
# see improper rule in A.M. No. 00-06-09-SC, 00-6-09-sc
# see rules which can't be found: 04-11-09-sc, 00-9-03-sc
# to do: 07-9-12-sc (amparo), 01-2-04-SC (interim corporate), 04-9-07-sc (sec), A.M. No. 03-8-02-sc (exec judge), 02-1-18-sc (children in conflict)
rule_bm = SerialPattern(
    cat=StatuteSerialCategory.BarMatter,
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
    cat=StatuteSerialCategory.CircularSC,
    regex_bases=[
        add_num(r"SC\s+Circular"),  # used in codifications
    ],
    regex_serials=[r"19"],
    matches=["SC Circular No. 19"],
    excludes=["SC Circular No. 1"],
)
oca_cir = SerialPattern(
    cat=StatuteSerialCategory.CircularOCA,
    regex_bases=[
        add_num(r"OCA\s+Circular"),  # used in codifications
    ],
    regex_serials=[r"39-02"],
    matches=["OCA Circular No. 39-02"],
    excludes=["SC Circular No. 39"],
)
rule_reso = SerialPattern(
    cat=StatuteSerialCategory.ResolutionEnBanc,
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
        veto,
        rule_reso,
    ]
)
