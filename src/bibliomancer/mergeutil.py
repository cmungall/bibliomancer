"""
Utilities for merging bibliographic entries.

TODO: Reuse more core LinkML features.
"""

import logging
from typing import Iterable, Iterator

from linkml_runtime import SchemaView

from bibliomancer.datamodel import SCHEMA_PATH
from bibliomancer.datamodel.biblio import Entry
from bibliomancer.utilities import entry_unique_keys, index_entries


logger = logging.getLogger(__name__)


def merge_entries_from(target_entries: Iterable[Entry], source_entries: Iterable[Entry], cols=None, overwrite=True):
    """
    Merge two lists of entries.

    >>> doi = "10.48550/2103.00001"
    >>> src = Entry(title="t1", doi=doi, journal="j1")
    >>> tgt = Entry(title="t1", doi=doi)
    >>> merge_entries_from([tgt], [src], cols=["journal"])
    >>> (tgt.journal, tgt.doi, tgt.title)
    ('j1', '10.48550/2103.00001', 't1')

    :param target_entries:
    :param source_entries:
    :return:
    """
    target_entries = list(target_entries)
    source_entries = list(source_entries)
    target_index = index_entries(target_entries)
    source_index = index_entries(source_entries)
    for unique_key, source_inner_index in source_index.items():
        target_inner_index = target_index.get(unique_key, {})
        if not target_inner_index:
            # logger.warning(f"Key {unique_key} not found in target")
            continue
        for tpl, source_entries in source_index.get(unique_key, {}).items():
            if len(source_entries) > 1:
                raise ValueError(
                    f"Multiple entries with key {unique_key} = {tpl}" f"found in source: {len(source_entries)}"
                )
            source_entry = source_entries[0]
            target_entries = target_inner_index.get(tpl, [])
            if len(target_entries) > 1:
                raise ValueError(f"Multiple entries with key {unique_key} found in target")
            if target_entries:
                target_entry = target_entries[0]
                if cols:
                    cols_to_copy = cols
                else:
                    cols_to_copy = [k for k in source_entry.model_fields if k not in unique_key]
                for col in cols_to_copy:
                    v = getattr(source_entry, col, None)
                    if v is not None:
                        curr_v = getattr(target_entry, col, None)
                        if curr_v is not None:
                            if curr_v != v:
                                if not overwrite:
                                    continue
                                logger.info(f"Overwriting {col} in {target_entry} with {v}")
                        setattr(target_entry, col, v)
