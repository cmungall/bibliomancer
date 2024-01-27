"""
Map entries from one schema to another.

TODO: replace using YAML files and linkml-transformer
"""

import logging
from functools import lru_cache
from typing import Iterable, Dict, Any

from bibliomancer.datamodel import FROM_PAPERPILE_TRANSFORMER_PATH
from bibliomancer.datamodel.enums import BiblioSchemaEnum
from linkml_transformer.session import Session

logger = logging.getLogger(__name__)

MAPPINGS_FROM = {
    BiblioSchemaEnum.PAPERPILE: {
        "type": "Item type",
        "title": ["Title", "Dataset name"],
        "authors": "Authors",
        "journal": "Journal",
        "repository": "Source",
        "conference_proceedings": "Proceedings title",
        "urls": "URLs",
        "doi": "DOI",
        "pmid": "PMID",
        "pmcid": "PMC ID",
        "arxiv_id": "Arxiv ID",
        "year": "Publication year",
        "volume": "Volume",
        "issue": "Issue",
        "pages": "Pages",
    },
}

# Mappings to DataCite
# https://support.datacite.org/docs/datacite-metadata-schema-44
ARTICLE_TYPE_ALIASES = {
    "Preprint": ["Preprint Manuscript"],
    "JournalArticle": ["Journal Article", "Review"],
    "ConferencePaper": ["Conference Paper"],
    "BookChapter": ["Book Chapter"],
    "Dataset": ["Dataset"],
    "Dissertation": ["Thesis"],
    "Software": ["Computer Program"],
    "Report": ["Report"],
    "Audiovisual": ["Video or Film"],
}


@lru_cache
def mapping_spec():
    tr_session = Session()
    tr_session.set_object_transformer(FROM_PAPERPILE_TRANSFORMER_PATH)


def map_entries(entries: Iterable[Dict[str, Any]], source_schema: BiblioSchemaEnum = None) -> Iterable[Dict[str, Any]]:
    """
    Map a list of entries to the export schema.

    :param entries:
    :param source_schema:
    :return:
    """
    for entry in entries:
        yield map_entry(entry, source_schema)


def map_entry(entry: Dict[str, Any], source_schema: BiblioSchemaEnum = None, exclude_none=True) -> Dict[str, Any]:
    """
    Map a single entry to the export schema.

    Defaults to mapping from paperpile; this may change

    >>> entry = {"Title": "My Paper", "Authors": ["Me M"],
    ...          "Journal": "foo studies", "Publication year": "2020",
    ...          "Issue": "1", "Volume": "1", "Pages": "1-2",
    ...          "Item type": "Journal Article"}
    >>> simple = map_entry(entry)
    >>> simple['type']
    'JournalArticle'
    >>> simple['local_id']
    '1(1):1-2'
    >>> simple['authors']
    ['Me M']
    >>> simple['year']
    '2020'
    >>> simple['title']
    'My Paper'
    >>> simple['journal']
    'foo studies'
    >>> simple['volume']
    '1'
    >>> simple['issue']
    '1'
    >>> simple['pages']
    '1-2'

    >>> map_entry({"Publication year": "2020", "Item type": "Journal Article"})
    {'type': 'JournalArticle', 'year': '2020'}

    :param entry:
    :param schema:
    :return:
    """
    if source_schema is None:
        source_schema = BiblioSchemaEnum.PAPERPILE
    if source_schema not in MAPPINGS_FROM:
        raise ValueError(f"Unsupported schema: {source_schema}")
    mappings = MAPPINGS_FROM[source_schema]

    def lookup(key):
        if isinstance(key, list):
            toks = [entry.get(k, None) for k in key]
            serialized = " ".join([t for t in toks if t is not None])
            if serialized:
                return serialized
            else:
                return None
        elif "{" in key:
            return key.format(**entry)
        else:
            return entry.get(key, None)

    mapped_entry = {k: lookup(v) for k, v in mappings.items()}
    if exclude_none:
        mapped_entry = {k: v for k, v in mapped_entry.items() if v is not None}
    if "type" not in mapped_entry:
        raise ValueError(f"Missing type in entry: {mapped_entry}")
    if mapped_entry["type"] not in ARTICLE_TYPE_ALIASES:
        for alias, values in ARTICLE_TYPE_ALIASES.items():
            if mapped_entry["type"] in values:
                mapped_entry["type"] = alias
                break
    if mapped_entry["type"] not in ARTICLE_TYPE_ALIASES:
        logger.warning(f"Unknown article type: {mapped_entry['type']}")
    typ = mapped_entry["type"]
    [volume, issue, pages] = [mapped_entry.get(k, None) for k in ["volume", "issue", "pages"]]
    if not volume and issue and pages:
        volume = mapped_entry["year"]
    if volume and issue and pages:
        mapped_entry["local_id"] = f"{volume}({issue}):{pages}"
    elif (volume or issue or pages) and typ == "JournalArticle":
        logger.warning(f"Missing volume, issue, or pages: {volume}, {issue}, {pages} in {mapped_entry['title']}")
    return mapped_entry
