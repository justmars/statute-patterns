import pytest

from statute_patterns.components.short import get_short


@pytest.mark.parametrize(
    "nodes, checked",
    [
        (
            [
                {
                    "item": "Container 1",
                    "caption": "Preliminary Title",
                    "units": [
                        {
                            "item": "Chapter 1",
                            "caption": "Effect and Application of Laws",
                            "units": [
                                {
                                    "item": "Article 1",
                                    "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)\n',  # noqa: E501
                                },
                                {
                                    "item": "Article 2",
                                    "content": "Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)\n",  # noqa: E501
                                },
                                {
                                    "item": "Article 3",
                                    "content": "Ignorance of the law excuses no one from compliance therewith. (2)\n",  # noqa: E501
                                },
                            ],
                        }
                    ],
                }
            ],
            "Civil Code of the Philippines",
        ),
        (
            [
                {
                    "item": "Section 1",
                    "caption": None,
                    "content": "Sample content",
                }
            ],
            None,
        ),
    ],
)
def test_get_short(nodes, checked):
    assert get_short(nodes) == checked
