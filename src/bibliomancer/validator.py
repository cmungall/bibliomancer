"""
Validator for bibliomancer entries.

TODO: make this a LinkML plugin
"""

from typing import Iterable, Dict, Any, Iterator, Union

from linkml.validator import Validator, JsonschemaValidationPlugin
from linkml.validator.report import ValidationResult, Severity

from bibliomancer.datamodel import biblio as bibm, SCHEMA_PATH
from bibliomancer.utilities import entry_unique_keys

UNIQUE_KEYS = [
    ["doi"],
    ["pmid"],
    ["pmcid"],
    ["arxiv_id"],
    ["isbn"],
    ["urls"],
    ["title"],  # deliberately strict - remove Preprint if surpassed
]


def validate_entries_iter(
    entries: Iterable[Union[bibm.Entry, Dict[str, Any]]], report_fields=None, partial=False, make_title_unique=True
) -> Iterator[ValidationResult]:
    """
    Validate a list of entries.

    Currently the only logic here is to check for duplicate entries.

    >>> entries = [{'doi': '10.48550/2103.00001'}, {'doi': '10.48550/2103.00001'}]
    >>> for err in validate_entries_iter(entries, partial=True):
    ...  print(err.message)
    Duplicate entries for ('doi',): ('10.48550/2103.00001',)

    >>> list(validate_entries_iter([{'doi': '10.48550/2103.00001'}, {'doi': '10.48550/2103.00002'}], partial=True))
    []

    >>> for err in validate_entries_iter([{}]):
    ...  print(err.message)
    'title' is a required property...


    :param entries:
    :param report_fields:
    :param partial:
    :param make_title_unique:
    :return:
    """
    validation_plugins = [JsonschemaValidationPlugin(closed=True)]
    validator = Validator(SCHEMA_PATH, validation_plugins=validation_plugins)
    # convert to dicts
    entries = [entry.model_dump(exclude_none=True) if isinstance(entry, bibm.Entry) else entry for entry in entries]
    if not partial:
        for entry in entries:
            for error in validator.iter_results(entry, target_class="Entry"):
                yield error

    # UC check
    def _err(msg: str):
        yield ValidationResult(message=msg, type="bespoke", severity=Severity.ERROR)

    unique_keys = entry_unique_keys()
    if make_title_unique:
        unique_keys.append(("title",))
    for key_tuple in unique_keys:
        # TODO: this should be a generic LinkML plugin
        values = set()
        for entry in entries:

            def _v(k):
                v = entry.get(k, None)
                if not v or v == [""]:
                    return None
                elif isinstance(v, list):
                    return tuple(v)
                else:
                    return v

            value = tuple(_v(key) for key in key_tuple)
            if not all(v for v in value):
                continue
            if value in values:
                msg = f"Duplicate entries for {key_tuple}: {value}"
                if report_fields:
                    msg += f" ({', '.join(entry.get(field, '') for field in report_fields)})"
                yield from _err(msg)
            values.add(value)
    for entry in entries:
        # TODO: replace with a rule
        if entry.get("type", None) == "JournalArticle":
            jrnl = entry.get("journal", None)
            if jrnl.lower() == "medrxiv" or jrnl.lower() == "biorxiv" or jrnl.lower().startswith("f1000"):
                yield from _err(f"Preprint in journal field: {jrnl}, {entry.get('Title', None)}")
