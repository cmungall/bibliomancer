"""Demo version test."""

import pytest

from bibliomancer.validator import validate_entries_iter


@pytest.mark.parametrize(
    "objects,passes",
    [
        ([{}], False),
        ([{"title": "test"}], True),
        ([{"doi": "10.48550/2103.00001"}, {"doi": "10.48550/2103.00001"}], False),
        ([{"title": "t1", "journal": "j1"}, {"title": "t1", "journal": "j1"}], False),
    ],
)
def test_validator(objects, passes):
    results = list(validate_entries_iter(objects))
    if passes:
        assert not results, f"Unexpected validation failure: {results}"
    else:
        assert results, "Unexpected validation pass"
