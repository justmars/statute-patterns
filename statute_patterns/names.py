from .components import Rule, StatuteSerialCategory
from .models import NamedPattern, NamedPatternCollection
from .recipes import CONST, ROC, SP_CIVIL, SP_COMMERCE, SP_PENAL


def make_spanish(name: str, regex: str):
    return NamedPattern(
        name=f"Old {name.title()} Code",
        regex_base=regex,
        rule=Rule(
            cat=StatuteSerialCategory.Spain,
            id=name,
        ),
    )


spain_civil = make_spanish("civil", SP_CIVIL)
spain_commerce = make_spanish("commerce", SP_COMMERCE)
spain_penal = make_spanish("penal", SP_PENAL)
spain_codes = [spain_civil, spain_commerce, spain_penal]
civ1950 = NamedPattern(
    name="Civil Code of 1950",
    regex_base=r"""
        (?: (?:New|NEW|The|THE)\s)?
        (?: (?<![Ss]panish\s)(?<![Oo]ld\s))
        (Civil|CIVIL)\s+(Code|CODE)
        (?: (?:\s+of\s+the\s+Philippines)|(?:\s+of\s+1950))?
        (?: (?!\s+of\s+1889))
    """,
    rule=Rule(
        cat=StatuteSerialCategory.RepublicAct,
        id="386",
    ),
    matches=[
        "NEW CIVIL CODE",
        "The Civil Code of the Philippines",
        "Civil Code of 1950",
    ],
    excludes=[
        "Spanish Civil Code",
        "OLD CIVIL CODE",
        "The new Civil Code of 1889",
    ],
)
rpc1930 = NamedPattern(
    name="Revised Penal Code",
    regex_base=r"""
        (?: (?:The|THE)\s)?
        (?: (?<![Ss]panish\s)(?<![Oo]ld\s))
        (Revised|REVISED)\s+(Penal|PENAL)\s+(Code|CODE)
        (?: (?:\s+of\s+the\s+Philippines)|(?:\s+\(RPC\)))?
    """,
    rule=Rule(
        cat=StatuteSerialCategory.Act,
        id="3815",
    ),
    matches=[
        "Revised Penal Code (RPC)",
        "The Revised Penal Code of the Philippines",
        "Revised Penal Code",
    ],
    excludes=[
        "The Penal Code",
        "OLD PENAL CODE",
        "The Spanish Penal Code",
    ],
)


def make_const(year: int):
    return NamedPattern(
        name=f"{year} Constitution",
        regex_base=rf"{year}\s+(?:{CONST})",
        rule=Rule(
            cat=StatuteSerialCategory.Constitution,
            id=f"{year}",
        ),
    )


const_1987: NamedPattern = make_const(1987)
const_1973: NamedPattern = make_const(1973)
const_1935: NamedPattern = make_const(1935)
const_years = [const_1987, const_1973, const_1935]


def make_roc(year: int):
    return NamedPattern(
        name=f"{year} Rules of Court",
        regex_base=rf"{year}\s+(?:{ROC})",
        rule=Rule(
            cat=StatuteSerialCategory.RulesOfCourt,
            id=f"{year}",
        ),
    )


roc_1918 = make_roc(1918)
roc_1964 = make_roc(1964)
roc_1940 = make_roc(1940)
roc_years = [roc_1964, roc_1940, roc_1918]


corpcode_old = NamedPattern(
    name="Corporation Code of 1980",
    regex_base=r"""
        (?: (?:The|THE)\s)?
        (?: (?<![Rr]evised\s)(?<!REVISED\s))
        (?: Corporation|CORPORATION)\s+(?:Code|CODE)
        (?: (?:\s+of\s+the\s+Philippines)|(?:\s+of\s+1980))?
    """,
    rule=Rule(
        cat=StatuteSerialCategory.BatasPambansa,
        id="68",
    ),
    matches=[
        "THE CORPORATION CODE",
        "Corporation Code of 1980",
        "Corporation Code of the Philippines",
    ],
    excludes=["Revised Corporation Code"],
)
corpcode_revised = NamedPattern(
    name="Corporation Code of 2021",
    regex_base=r"""
        (?:[Rr]evised|REVISED)\s+(?:Corporation|CORPORATION)\s+(?:Code|CODE)
        (?: (?:\s+of\s+the\s+Philippines)|(?:\s+of\s+2021))?
    """,
    rule=Rule(
        cat=StatuteSerialCategory.RepublicAct,
        id="11232",
    ),
    matches=[
        "Revised Corporation Code",
        "Revised Corporation Code of the Philippines",
        "Revised Corporation Code of 2021",
    ],
    excludes=["The Corporation Code"],
)


cpr = NamedPattern(
    name="Code of Professional Responsibility 1988",
    regex_base=r"""
        (?:
            (?:Code|CODE)
            \s+
            (?:of|Of|OF)
            \s+
            (?:Professional|PROFESSIONAL)
            \s+
            (?:Responsibility|RESPONSIBILITY)
            (?:\s+\(CPR\))?
        )|
        (?:
            of\s+
            the\s+
            CPR
        )
    """,
    rule=Rule(
        cat=StatuteSerialCategory.RulesOfCourt,
        id="cpr",
    ),
    matches=[
        "Code of Professional Responsibility (CPR)",
        "Code of Professional Responsibility",
        "CODE OF PROFESSIONAL RESPONSIBILITY",
        "of the CPR",
    ],
    excludes=["The Corporation Code"],
)

NamedRules = NamedPatternCollection(
    collection=[civ1950, rpc1930, corpcode_old, corpcode_revised, cpr]
    + spain_codes
    + const_years
    + roc_years
)
