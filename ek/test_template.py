import pytest

from ek.template import populate_template


@pytest.mark.parametrize(
    ("template", "kwargs", "expected"),
    [
        ("foo", dict(bar="bar"), "foo"),
        ("foo-{bar}", dict(bar="bar"), "foo-bar"),
        ("foo-{bar}-{baz}", dict(bar="bar", baz="baz"), "foo-bar-baz"),
        ("foo-{bar}-{baz}", dict(bar="bar", baz="baz", biff="biff"), "foo-bar-baz"),
    ],
)
def test_populate_template(template, kwargs, expected):
    assert populate_template(template, **kwargs) == expected
