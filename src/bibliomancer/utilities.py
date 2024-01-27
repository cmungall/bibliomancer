"""
General utilities for bibliomancer.
"""

import re
from collections import defaultdict
from functools import lru_cache
from typing import Tuple, List, Dict, Union, Iterable

from linkml_runtime import SchemaView

from bibliomancer.datamodel import SCHEMA_PATH
from bibliomancer.datamodel.biblio import Entry


def author_matches(author: str, query: str, partial=False) -> bool:
    """
    Check if an author matches a query.

    >>> author_matches("Foo", "Foo")
    True
    >>> author_matches("Foo", "Bar")
    False
    >>> author_matches("Foo, CJ", "Foo, C")
    False
    >>> author_matches("Foo, CJ", "Foo, CJ?")
    True
    >>> author_matches("Foo, C", "Foo, CJ?")
    True

    :param author: Author to check.
    :param query: Author name to check - exact str or regex.
    :param partial: If True, allow partial matches.
    :return:
    """
    if query == author:
        return True
    if not partial:
        query = "^" + query + "$"
    if re.match(query, author):
        return True
    return False


@lru_cache
def metamodel_schemaview() -> SchemaView:
    """
    Get the SchemaView for the metamodel.

    :return:
    """
    return SchemaView(SCHEMA_PATH)


@lru_cache
def entry_unique_keys() -> List[Tuple[str]]:
    """
    Get the unique keys for the Entry class.

    :return:
    """
    sv = metamodel_schemaview()
    ec = sv.get_class("Entry")
    keys = []
    for unique_key in ec.unique_keys.values():
        keys.append(tuple(unique_key.unique_key_slots))
    return keys


def as_entry_objects(entries: Iterable[Union[dict, Entry]]) -> List[Entry]:
    """
    Convert a list of dicts to Entry objects.

    :param entries:
    :return:
    """
    return [Entry(**e) if isinstance(e, dict) else e for e in entries]


def index_entries(entries: List[Union[dict, Entry]], strict=True) -> Dict[Tuple, Dict[Tuple, List[Entry]]]:
    """
    Index entries by keys.

    >>> doi1 = "10.48550/2103.00001"
    >>> doi2 = "10.48550/2103.00002"
    >>> entries = [Entry(title="t1", doi=doi1), Entry(title="t2", doi=doi2)]
    >>> ix = index_entries(entries)
    >>> ix[("doi",)][(doi1,)][0].title
    't1'

    >>> list(ix[("pmid",)])
    []

    Note currently only indexes unique keys, so size of inner list is always 1.

    :param entries:
    :return:
    """
    index = defaultdict(dict)

    for unique_key in entry_unique_keys():
        index[unique_key] = defaultdict(list)
        for entry in entries:
            tpl = tuple(getattr(entry, k, None) for k in unique_key)
            if any(v is None for v in tpl):
                continue
            vals = index[unique_key][tpl]
            if strict and len(vals) > 0:
                raise ValueError(f"Multiple entries with key {unique_key} = {tpl} found: {vals}")
            vals.append(entry)
    return index
