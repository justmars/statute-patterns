import toml

import statute_patterns


def test_version():
    assert (
        toml.load("pyproject.toml")["tool"]["poetry"]["version"]
        == statute_patterns.__version__
    )
