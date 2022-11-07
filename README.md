# Statute Patterns

Extract path-based rules from given Philippine legal text.

```python

>>> text = """
"The Civil Code of the Philippines, the old Spanish Civil Code; Rep Act No. 386"
"""

>>> from statute_patterns import extract_rule, extract_rules, count_rules

>>> r = extract_rule(text)  # get the first matching rule with helper to extract path (assuming local statute folder exists )
>>> r
Rule(cat='ra', id='386')
>>> r.get_path(path_to_statutes)
Path().home().joinpath(path_to_statutes/"ra"/"386")

>>> extract_rules(text) # get all rules
[
    Rule(cat='ra', id='386'),
    Rule(cat='ra', id='386'),
    Rule(cat='spain', id='civil')
]
>>> count_rules(text): # get unique rules with counts
[
    {'cat': 'ra', 'id': '386', 'mentions': 2},
    {'cat': 'spain', 'id': 'civil', 'mentions': 1}
]
```
