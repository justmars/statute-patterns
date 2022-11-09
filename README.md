# Statute Patterns

## Title matching of rules

Extract title of rules from given Philippine statutory text.

The title, parsed through a `Rule` object, corresponds to a local path to separate library from which the contents of the rule can be extracted from.

```python
# use sample text for demo
>>> text = """The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"""

# get first matching rule with helper to extract path
from statute_patterns import extract_rule
>>> rule_obj = extract_rule(text)
>>> rule_obj
Rule(cat='ra', id='386')


# get all rules
>>> from statute_patterns import extract_rules
>>> extract_rules(text)
[
    Rule(cat='ra', id='386'),
    Rule(cat='ra', id='386'),
    Rule(cat='spain', id='civil')
]


# get unique rules with counts
>>> from statute_patterns import count_rules
>>> count_rules(text):
[
    {'cat': 'ra', 'id': '386', 'mentions': 2},
    {'cat': 'spain', 'id': 'civil', 'mentions': 1}
]
```

## Loading files from rules

Each rule corresponds to a possible set of folders in a local directory `/statutes`.

Each rule belongs to a *StatuteSerialCategory*. The present *StatuteSerialCategory* is an Enum with the following members. The value of each member is the path to such category.

```python
>>>StatuteSerialCategory
<enum 'StatuteSerialCategory'>
>>>StatuteSerialCategory._member_map_
{
    'RepublicAct': <StatuteSerialCategory.RepublicAct: 'ra'>,
    'CommonwealthAct': <StatuteSerialCategory.CommonwealthAct: 'ca'>,
    'Act': <StatuteSerialCategory.Act: 'act'>,
    'Constitution': <StatuteSerialCategory.Constitution: 'const'>,
    'Spain': <StatuteSerialCategory.Spain: 'spain'>,
    'BatasPambansa': <StatuteSerialCategory.BatasPambansa: 'bp'>,
    'PresidentialDecree': <StatuteSerialCategory.PresidentialDecree: 'pd'>,
    'ExecutiveOrder': <StatuteSerialCategory.ExecutiveOrder: 'eo'>,
    'LetterOfInstruction': <StatuteSerialCategory.LetterOfInstruction: 'loi'>,
    'VetoMessage': <StatuteSerialCategory.VetoMessage: 'veto'>,
    'RulesOfCourt': <StatuteSerialCategory.RulesOfCourt: 'roc'>,
    'BarMatter': <StatuteSerialCategory.BarMatter: 'rule_bm'>,
    'AdministrativeMatter': <StatuteSerialCategory.AdministrativeMatter: 'rule_am'>,
    'ResolutionEnBanc': <StatuteSerialCategory.ResolutionEnBanc: 'rule_reso'>,
    'CircularOCA': <StatuteSerialCategory.CircularOCA: 'oca_cir'>,
    'CircularSC': <StatuteSerialCategory.CircularSC: 'sc_cir'>
}
```

So to point to the Civil Code of the Philippines, this would be represented by the following path `statutes/ra/386` where *ra* is the StatuteSerialCategory and *386* is the serial id.

Knowing the path to a rule, we can extract the rules contents.

```python
>>> rule_obj # example from above
Rule(cat='ra', id='386')
>>> list(rule_obj.extract_folders(<path/to/statutes>))
[PosixPath('.../statutes/ra/386')]
```

There can be more than one path since in exceptional cases, the combination of *category* + *serial id* does not yield a unique rule.

We can extract the details of the rule with the `StatuteDetails.from_rule()` also accessible via `Rule.get_details()`:

```python
>>>from statute_patterns import StatuteDetails
>>>StatuteDetails.from_rule(rule_obj, <path/to/statutes>) # or rule_obj.get_details(<path/to/details>)
StatuteDetails(
    created=1665225124.0644598,
    modified=1665225124.0644598,
    rule=Rule(cat='ra', id='386'),
    title='An Act to Ordain and Institute the Civil Code of the Philippines',
    description='Republic Act No. 386',
    id='ra-386-june-18-1949',
    emails=['maria@abcxyz.law', 'fernando@abcxyz.law'],
    date=datetime.date(1949, 6, 18),
    variant=1,
    units=[
        {
            'item': 'Container 1',
            'caption': 'Preliminary Title',
            'units': [
                {
                    'item': 'Chapter 1',
                    'caption': 'Effect and Application of Laws',
                    'units': [
                        {
                            'item': 'Article 1',
                            'content': 'This Act shall be known as the "Civil Code of the Philippines." (n)\n'
                        },
                        {
                            'item': 'Article 2',
                            'content': 'Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)\n'
                        },
                        ...
                    ]
                },
                ...
            ]
        },
        ...
    ],
    titles=[
        StatuteTitle(
            statute_id='ra-386-june-18-1949',
            category='alias',
            text='New Civil Code'
        ),
        StatuteTitle(
            statute_id='ra-386-june-18-1949',
            category='alias',
            text='Civil Code of 1950'
        ),
        StatuteTitle(
            statute_id='ra-386-june-18-1949',
            category='official',
            text='An Act to Ordain and Institute the Civil Code of the Philippines'
        ),
        StatuteTitle(
            statute_id='ra-386-june-18-1949',
            category='serial',
            text='Republic Act No. 386'
        )
    ]
)
```
