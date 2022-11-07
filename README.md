# Statute Patterns

Extract path-based rules from given Philippine legal text.

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

# ensure valid local path exists to extract data from such path, use the first sample rule above
>>> from statute_patterns import load_rule_data
>>> path_to_folder = rule_obj.get_path(path_to_statutes)
Path().home().joinpath("path_to_statutes/ra/386")
>>> load_rule_data(rule_obj, path_to_statutes)
{
    'created': 1665225124.0644598,
    'modified': 1665225124.0644598,
    'id': 'ra-386-june-18-1949',
    'emails': ['maria@abcxyz.law', 'fernando@abcxyz.law'],
    'date': datetime.date(1949, 6, 18),
    'variant': None,
    'units': [
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
                    ]
                },
                ...
            ]
        },
        ...
    ],
    'titles': [
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
}
```
