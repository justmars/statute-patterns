# Summary

## Match Titles

Detect titles of Philippine statutes when found in text.

```py
# imagine messy legalese with citations
>>> text = """
A.M. No. 02-11-10-SC or the Rules on Declaration of Absolute;
Administrative Order No. 3 by enacting A.M. No. 99-10-05-0;
Parenthetically, under these statutes [referring to RA Nos. 965 and 2630]
Commonwealth Act (C.A.) No. 613, otherwise known as
the <em>Philippine Immigration Act of 1940</em>; see also
Republic Act No. 386
"""

>>> from statute_patterns import extract_rules
>>> list(extract_rules(text))
[Rule(cat='rule_am', id='02-11-10-sc'),
 Rule(cat='rule_am', id='99-10-05-0'),
 Rule(cat='ra', id='965'),
 Rule(cat='ra', id='2630'),
 Rule(cat='ca', id='613'),
 Rule(cat='ra', id='386')]
```

## Extract Content

Extract [`Statute Details`][statute-details] of a properly formatted file found in `/statutes/ra/386/1.yml`:

```py
>>> from statute_patterns import StatuteDetails
>>> f = STATUTE_DIR.glob("ra/386/**/1.yml")
>>> StatuteDetails.from_file(file)
'ra/386/1949-06-18/1.yml'
>>> obj.units
[{'item': 'Container 1',
  'caption': 'Preliminary Title',
  'units': [{'item': 'Chapter 1',
    'caption': 'Effect and Application of Laws',
    'units': [{'item': 'Article 1',
      'content': 'This Act shall be known as the "Civil Code of the Philippines." (n)'},
     {'item': 'Article 2',
      'content': 'Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)'},
      ... # more nested units
    ]}]
}]
>>> obj.titles
[StatuteTitle(category=<StatuteTitleCategory.Alias: 'alias'>, text='New Civil Code'),
 StatuteTitle(category=<StatuteTitleCategory.Alias: 'alias'>, text='Civil Code of 1950'),
 StatuteTitle(category=<StatuteTitleCategory.Short: 'short'>, text='Civil Code of the Philippines'),
 StatuteTitle(category=<StatuteTitleCategory.Serial: 'serial'>, text='Republic Act No. 386'),
 StatuteTitle(category=<StatuteTitleCategory.Official: 'official'>, text='An Act to Ordain and Institute the Civil Code of the Philippines')]
```
