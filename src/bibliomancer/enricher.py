"""
Enrichment and repair functionality.

In future some of this will be replaced by LinkML rules.
"""

import re
from typing import Any, Dict, Iterator, Iterable, Union

from bibliomancer import eutils
from bibliomancer.io import load_file_iter, write_file
from bibliomancer.utilities import author_matches, metamodel_schemaview
from bibliomancer.datamodel import biblio as bibm

ARXIV_DOI_PREFIX = "10.48550"
BIORXIV_DOI_PREFIX = "10.1101"
CHEMRXIV_DOI_PREFIX = "10.26434"

RULES = [
    {
        "name": "doi_from_arxiv",
        "assigns": {
            "doi": ARXIV_DOI_PREFIX + "/{arxiv_id}",
        },
        "sources": ["arxiv_id"],
        "tests": [
            {"input": {"arxiv_id": "2103.00001"}, "output": {"arxiv_id": "2103.00001", "doi": "10.48550/2103.00001"}},
        ],
    },
    {
        "name": "PMC_from_PMID",
        "assigns": {
            "pmcid": lambda pmid: eutils.pmid_to_pmc(pmid),
        },
        "sources": ["pmid"],
        "tests": [
            {"input": {"pmid": "37389415"}, "output": {"pmid": "37389415", "pmcid": "PMC10336030"}},
        ],
    },
    {
        "name": "infer_journal",
        "sources": [],
        "tests": [
            {"input": {"arxiv_id": "2103.00001"}, "output": {"arxiv_id": "2103.00001", "journal": "arXiv"}},
        ],
    },
]


def repair_file(input_file: str, output_file: str, input_format: str = None, output_format: str = None) -> None:
    """
    Repair a file.

    :param input_file:
    :param output_file:
    :return:
    """
    entries = load_file_iter(input_file, input_format)
    repaired_entries = [bibm.Entry(**e) for e in repair_all_iter(entries)]
    write_file(repaired_entries, output_file, output_format)


def repair_all_iter(entries: Iterable[Union[bibm.Entry, Dict[str, Any]]]) -> Iterator[bibm.Entry]:
    """
    Repair a list of entries.

    Accepts dicts or Entry objects - this is because we may want to repair partial
    entries.

    :param entries: can be dicts or Entry objects
    :return: iterator of repaired entries, as dicts
    """
    for entry in entries:
        yield repair(entry)


def repair(entry: Union[bibm.Entry, Dict[str, Any]], replace=False, rules=None) -> Dict[str, Any]:
    """
    Repair an entry.

    Accepts dicts or Entry objects - this is because we may want to repair partial
    entries.

    ArXiv rule:

    >>> repair({"arxiv_id": "2103.00001"})
    {'arxiv_id': '2103.00001', 'doi': '10.48550/2103.00001', 'journal': 'arXiv'}

    >>> repair(bibm.Entry(title="test", arxiv_id="2103.00001"))
    {'title': 'test', 'arxiv_id': '2103.00001', 'doi': '10.48550/2103.00001', 'journal': 'arXiv'}

    >>> repair(bibm.Entry(title="test", urls=["https://ceur-ws.org/Vol-2814/paper-01.pdf"]))
    {'title': 'test', 'urls': ['https://ceur-ws.org/Vol-2814/paper-01.pdf'], 'ceur_ws_url': 'https://ceur-ws.org/Vol-2814/paper-01.pdf'}

    By default, assume existing value is correct:

    >>> repair({'arxiv_id': '2103.00001', 'doi': 'BAD DOI'})
    {'arxiv_id': '2103.00001', 'doi': 'BAD DOI', 'journal': 'arXiv'}

    If replace is True, then replace existing value:

    >>> repair({'arxiv_id': '2103.00001', 'doi': 'BAD DOI'}, replace=True)
    {'arxiv_id': '2103.00001', 'doi': '10.48550/2103.00001', 'journal': 'arXiv'}

    :param entry: dict or Entry object
    :param replace: replace existing values
    :param rules: rules to apply - applies all rules by default
    :return: repaired dict
    """
    sv = metamodel_schemaview()
    if isinstance(entry, bibm.Entry):
        entry = entry.model_dump(exclude_unset=True)
    entry = entry.copy()
    for rule in RULES:
        if rules and rule["name"] not in rules:
            continue
        vars = {normalize_key(k): entry.get(k, None) for k in rule["sources"]}
        if any(vars.values()):
            if replace or not any(entry.get(k, None) for k in rule["assigns"].keys()):
                entry.update({k: apply_assignment(v, vars) for k, v in rule["assigns"].items()})
    if not rules or "infer_urls" in rules:
        for slot in sv.all_slots().values():
            if slot.range == "uri":
                pattern = slot.pattern
                if pattern:
                    for url in entry.get("urls", []):
                        if re.match(pattern, url):
                            entry[slot.name] = url
                            break
    if not rules or "infer_journal" in rules:
        if "journal" not in entry:
            if "arxiv_id" in entry or ARXIV_DOI_PREFIX in entry.get("doi", ""):
                entry["journal"] = "arXiv"
            elif "biorxiv_id" in entry or BIORXIV_DOI_PREFIX in entry.get("doi", ""):
                entry["journal"] = "bioRxiv"
            elif "chemrxiv_id" in entry or CHEMRXIV_DOI_PREFIX in entry.get("doi", ""):
                entry["journal"] = "chemRxiv"
    return entry


def apply_assignment(spec: Any, vars: Dict[str, Any]) -> Any:
    """
    Apply an assignment.

    :param spec: either a function or a format string
    :param vars:
    :return:
    """
    if callable(spec):
        return spec(**vars)
    else:
        return spec.format(**vars)


def normalize_key(key: str) -> str:
    """
    Normalize a key to snake case.

    :param key:
    :return:
    """
    return key.replace(" ", "_").lower()


def annotate_author_position(
    entries: Iterable[Dict[str, Any]], author_query: str, overwrite=False
) -> Iterator[Dict[str, Any]]:
    """
    Annotate author position.

    :param entries:
    :param author_query:
    :param overwrite:
    :return:
    """
    for entry in entries:
        entry = entry.copy()
        authors = entry.get("authors", [])
        num_authors = len(authors)
        entry["num_authors"] = num_authors
        for i, author in enumerate(authors):
            if author_matches(author, author_query):
                entry["position"] = i + 1
                entry["rank"] = i if i + 1 < num_authors / 2 else -(num_authors - i)
                entry["significance"] = 1 - (abs(entry["rank"]) - 1) / num_authors
                if i == 0:
                    if num_authors == 1:
                        role = "sole"
                    else:
                        role = "lead"
                elif i == num_authors - 1:
                    role = "senior"
                elif i == num_authors - 2 and num_authors >= 8:
                    role = "co_senior"
                elif i == num_authors - 3 and num_authors >= 20:
                    role = "co_senior"
                elif i == 1 and num_authors >= 8:
                    role = "co_lead"
                else:
                    role = "contributor"
                if overwrite or "role" not in entry:
                    entry["role"] = role

        yield entry
