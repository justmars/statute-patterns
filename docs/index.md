# Summary

## Match Titles

Detect titles of Philippine statutory text from arbitrary text:

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

Generate a path to the title detected and extract its contents. This presumes a structured local path like so:

```yaml
/statutes
  /act # act of congress
  /ca # commonwealth act
  /ra # republic act
    /386 # ra 386 = civil code
      details.yaml # contains main file
      units.yaml (or ra386.yaml) # contains provisions
```

The _main_ `details.yaml` file should contain relevant metadata:

```yaml
numeral: '386' # serial id
category: ra  # category
law_title: An Act to Ordain and Institute the Civil Code of the Philippines # official title
date: June 18, 1949
aliases:
- New Civil Code # maps to alias
- Civil Code of 1950
emails:
- maria@abcxyz.law # email address of formatter
- fernando@abcxyz.law # can have multiple formatters
```

The _provisions_ `units.yaml` or `ra386.yaml` file should be properly nested:

```yaml
- item: Container 1
  caption: Preliminary Title
  units:
  - item: Chapter 1
    caption: Effect and Application of Laws
    units:
    - item: Article 1
      content: |
        This Act shall be known as the "Civil Code of the Philippines." (n)
    - item: Article 2
    ...
```

With the example above, it's possible to extract the [StatuteDetails](api-extract.md) of `/statutes/ra/386`:

```py
>>>r = Rule(cat='ra', id='386') # assign the Rule to `r`
>>>r(<path/to/statutes>) # get the base path to `/statutes`
StatuteDetails(
    created=1665225124.0644598,
    modified=1665225124.0644598,
    rule=Rule(cat='ra', id='386'),
    title='Republic Act No. 386',
    description='An Act to Ordain and Institute the Civil Code of the Philippines',
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
