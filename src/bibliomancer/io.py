"""
Load/Dump operations for different bibliographic formats.

By default loaders will map to the BIBM schema, and writers assume the BIBM schema.

TODO: reuse more core linkml features
"""

import csv
import logging
from pathlib import Path
from typing import Dict, Any, Union, TextIO, Iterator, Optional, Iterable, List

import bibliomancer.datamodel.biblio as bibm
from bibliomancer.datamodel.enums import BiblioSchemaEnum, BiblioSyntaxEnum
from bibliomancer.mapper import map_entry
from bibliomancer.utilities import as_entry_objects

logger = logging.getLogger(__name__)

FORMAT = Union[BiblioSyntaxEnum, str]


PAPERPILE_MULTIVALUED_SEPARATOR_MAP = {
    "Authors": ",",
    "Keywords": ";",
    "URLs": ";",
}

BIBM_MULTIVALUED_SEPARATOR_MAP = {
    "authors": "|",
    "urls": "|",
}


def inject_multivalued(entry: Dict[str, Any], separator_map: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Inject multivalued fields.

    >>> from bibliomancer.io import inject_multivalued
    >>> inject_multivalued({"Authors": "Me M, You Y"})
    {'Authors': ['Me M', 'You Y'], 'Authors_verbatim': 'Me M, You Y'}
    >>> inject_multivalued({"Authors": ""})
    {'Authors': [], 'Authors_verbatim': ''}

    :param entry:
    :param separator_map:
    :return:
    """
    if separator_map is None:
        separator_map = PAPERPILE_MULTIVALUED_SEPARATOR_MAP
    entry = entry.copy()
    for key, sep in separator_map.items():
        if key in entry and entry.get(key, None) is not None and isinstance(entry.get(key), str):
            entry[f"{key}_verbatim"] = entry[key]
            vals = entry[key].split(sep)
            if vals == [""]:
                vals = []
            entry[key] = vals
    return entry


def load_file(*args, **kwargs) -> List[bibm.Entry]:
    """
    Load a file.

    See load_file_iter for details.

    :param args:
    :param kwargs:
    :return:
    """
    return list(load_file_iter(*args, **kwargs))


def load_file_iter(
    input_file: Union[str, Path, TextIO], format: str = None, schema: Union[str, BiblioSchemaEnum] = None
) -> Iterator[bibm.Entry]:
    """
    Load a file.

    :param input_file:
    :param format:
    :return:
    """
    if isinstance(input_file, Path):
        input_file = str(input_file)
    if format is None:
        file_name = input_file if isinstance(input_file, str) else input_file.name
        format = file_name.split(".")[-1]
        logger.info(f"Inferring format {format} from file name {file_name}")
    if schema is None:
        schema = BiblioSchemaEnum.PAPERPILE
    if not isinstance(schema, BiblioSchemaEnum):
        schema = BiblioSchemaEnum(schema)
    if isinstance(input_file, str):
        with open(input_file, "r") as stream:
            yield from load_file_iter(stream, format=format, schema=schema)
            return
    if format == "csv":
        reader = csv.DictReader(input_file)
        if schema == BiblioSchemaEnum.PAPERPILE:
            mvmap = PAPERPILE_MULTIVALUED_SEPARATOR_MAP
        else:
            mvmap = BIBM_MULTIVALUED_SEPARATOR_MAP
        for row in reader:
            row = inject_multivalued(row, mvmap)
            row = {k: v for k, v in row.items() if v is not None and v != ""}
            if schema == BiblioSchemaEnum.PAPERPILE:
                yield bibm.Entry(**map_entry(row, source_schema=schema))
            else:
                yield bibm.Entry(**row)
    elif format == "json":
        import json

        entries = json.load(input_file)
        yield from as_entry_objects(entries)
    elif format == "yaml":
        import yaml

        entries = yaml.safe_load(input_file)
        yield from as_entry_objects(entries)
    else:
        raise ValueError(f"Unsupported format: {format}")


def write_file(
    entries: Union[Iterable[bibm.Entry], Dict],
    output_file: Union[str, TextIO, Path],
    format: Optional[FORMAT] = None,
    schema: Optional[BiblioSchemaEnum] = None,
) -> None:
    """
    Write a set of entries to a file.

    :param entries:
    :param output_file:
    :param format:
    :return:
    """
    if isinstance(output_file, Path):
        output_file = str(output_file)
    if isinstance(output_file, str):
        with open(output_file, "w") as stream:
            write_file(entries, stream, format)
            return
    if format is None:
        format = BiblioSyntaxEnum.CSV
    if not isinstance(format, BiblioSyntaxEnum):
        format = BiblioSyntaxEnum(format)
    entries = [e.model_dump() if isinstance(e, bibm.Entry) else e for e in entries]
    if format == BiblioSyntaxEnum.CSV:
        fieldnames = []
        for entry in entries:
            fieldnames.extend([k for k in entry.keys() if k not in fieldnames])
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            flatten_list(entry)
            if entry is None:
                entry = ""
            writer.writerow(entry)
    elif format == BiblioSyntaxEnum.YAML:
        import yaml

        yaml.dump(list(entries), output_file)
    elif format == BiblioSyntaxEnum.JSON:
        import json

        json.dump(list(entries), output_file)
    else:
        raise Exception(f"Unsupported format: {format}")


def flatten_list(entry: dict, list_delimiter="|"):
    for key, value in entry.items():
        if isinstance(value, list):
            entry[key] = list_delimiter.join(value)
