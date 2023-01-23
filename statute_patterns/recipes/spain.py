spanish_prefix = r"""
    \[?
        (?:
            (?:S|s)panish|
            (?:O|o)ld
        )
    \]?
"""

spanish_optional_year = r"""
    (?:
        \s+of\s+18\d{2}
    )?
"""

SP_CIVIL = rf"""
    (?:{spanish_prefix})
    \s+
    Civil
    \s+
    Code
    {spanish_optional_year}
"""

SP_COMMERCE = rf"""
    (?:{spanish_prefix})
    \s+
    Code
    \s+
    of
    \s+
    Commerce
    {spanish_optional_year}
"""


SP_PENAL = rf"""
    (?:{spanish_prefix}|(?:[T|t]he))
    \s+
    Penal
    \s+
    Code
    {spanish_optional_year}
"""
