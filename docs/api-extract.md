# Extraction

This presumes existence of a local path to a separate library where the contents of the rule can be extracted from.

## Extract Rules

::: statute_patterns.__main__.extract_rules

## Extract Rule

::: statute_patterns.__main__.extract_rule

## Count Rules

::: statute_patterns.__main__.count_rules

## Detail Rule

We can extract the details of the rule with the `StatuteDetails.from_rule()` also accessible via `Rule.get_details()`:

```py
>>>from statute_patterns import StatuteDetails
>>>StatuteDetails.from_rule(rule_obj, <path/to/statutes>) # or rule_obj.get_details(<path/to/details>)
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

### StatuteDetails

::: statute_patterns.StatuteDetails
