const_ph = r"""(?:Constitution(\s+of\s+the\s+Philippines)?)"""

const_title = r"""(?:
    (?:
        Phil\.?\s+
    )?
    Const
        (
            itution|
            \.
        )?
)"""

const_capped = r"""(?:
    (?:
        PHIL\.?\s+
    )?
    CONST
        (
            ITUTION|
            \.
        )?
)"""


CONST = "|".join([const_ph, const_capped, const_title])
