"""Demo version test."""

import pytest

from bibliomancer.utilities import index_entries, as_entry_objects
from bibliomancer.validator import validate_entries_iter


DOI1 = "10.48550/2103.00001"
DOI2 = "10.48550/2103.00002"
T = "JournalArticle"
J1 = "j1"
J2 = "j2"


@pytest.mark.parametrize(
    "entries,index_key,index_val,expected,valid",
    [
        ([{"title": "t1", "doi": DOI1}], ("doi",), (DOI1,), "t1", True),
        ([{"title": "t1", "doi": DOI1}], ("doi",), (DOI2,), None, True),
        ([{"title": "t1", "doi": DOI1}], ("pmid",), ("x",), None, True),
        ([{"title": "t1", "doi": DOI1}, {"title": "t2", "doi": DOI2}], ("doi",), (DOI1,), "t1", True),
        ([{"title": "t1", "doi": DOI1}, {"title": "t2", "doi": DOI2}], ("doi",), (DOI2,), "t2", True),
        (
            [{"title": "t1", "doi": DOI1, "journal": J1}, {"title": "t2", "doi": DOI2, "journal": J2}],
            ("doi",),
            (DOI2,),
            "t2",
            True,
        ),
        (
            [{"title": "t1", "doi": DOI1, "type": T}, {"title": "t2", "doi": DOI2, "type": T}],
            ("type", "title"),
            (T, "t1"),
            "t1",
            True,
        ),
        (
            [{"title": "t1", "doi": DOI1, "journal": J1}, {"title": "t2", "doi": DOI1, "journal": J2}],
            None,
            None,
            None,
            False,
        ),
    ],
)
def test_index(entries, index_key, index_val, expected, valid):
    entries = as_entry_objects(entries)
    if not valid:
        with pytest.raises(ValueError):
            ix = index_entries(entries)
        return
    ix = index_entries(entries)
    sub_index = ix[index_key]
    v = sub_index[index_val]
    if expected is not None:
        assert v[0].title == expected
    else:
        assert v is None or len(v) == 0
