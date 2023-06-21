# statute-patterns

![Github CI](https://github.com/justmars/statute-patterns/actions/workflows/main.yml/badge.svg)

Philippine statutory law pattern matching and unit retrieval; utilized in [LawSQL dataset](https://lawsql.com).

## Documentation

See [documentation](https://justmars.github.io/statute-patterns).

## Development

Checkout code, create a new virtual environment:

```sh
poetry add statute-patterns # python -m pip install statute-patterns
poetry update # install dependencies
poetry shell
```

## Some unit patterns

```json title="Convention used when desiring to exclude appropriation laws."
{
  "units": [
    {
        "item": "Container 1",
        "content": "Appropriation laws are excluded.",
    }
  ]
}
```


```json title="Convention used when no content found."
UNITS_NONE = [
    {
        "item": "Container 1",
        "content": "Individual provisions not detected.",
    }
]
```
