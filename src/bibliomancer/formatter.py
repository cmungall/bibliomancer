"""
Module for formatting bibliographic entries.

Currently only a single jinja2 template is supported, for generating markdown.

This can later be converted to HTML using pandoc.
"""

import re
from pathlib import Path
from typing import Iterable, Any, Dict, TextIO, List, Optional, Union

from jinja2 import Environment, FileSystemLoader

from bibliomancer.datamodel.enums import BiblioSchemaEnum
from bibliomancer.templates import TEMPLATE_DIR
import bibliomancer.datamodel.biblio as bibm


def highlight_authors(entry: bibm.Entry, authors: List[str]) -> bibm.Entry:
    """
    Highlight authors in a list of authors.

    >>> import bibliomancer.datamodel.biblio as bibm
    >>> entry = bibm.Entry(
    ...                    type="JournalArticle", title="My Paper",
    ...                    authors=["Me M"], journal="foo studies", year="2020", local_id="1(1)")
    >>> highlight_authors(entry, ["Me M"]).authors
    ['**Me M**']

    :param entry:
    :param authors:
    :return:
    """
    entry = bibm.Entry(**entry.model_dump())

    def matches(author: str) -> bool:
        for author_to_match in authors:
            if author_to_match == author:
                return True
            if re.match(author_to_match, author):
                return True
        return False

    entry.authors = [f"**{author}**" if matches(author) else author for author in entry.authors]
    return entry


def generate_markdown(
    entries: Union[Iterable[bibm.Entry], Dict],
    stream: TextIO,
    template_name: str = None,
    authors: Optional[List] = None,
    source_schema: BiblioSchemaEnum = None,
) -> None:
    """
    Generate markdown from a set of entries using Jinja2

    >>> import io
    >>> from bibliomancer.formatter import generate_markdown
    >>> entries = [ {"type": "JournalArticle", "title": "My Paper", "authors": ["Me M"], "journal": "foo studies", "year": "2020", "local_id": "1(1)"} ]
    >>> text_stream = io.StringIO()
    >>> generate_markdown(entries, text_stream)

    :param entries:
    :param stream:
    :return:
    """
    entries = [bibm.Entry(**e) if isinstance(e, dict) else e for e in entries]
    if template_name is None:
        template_name = "default.markdown"

    if authors:
        entries = [highlight_authors(entry, authors) for entry in entries]

    entries = sorted(
        entries, reverse=True, key=lambda x: (str(x.year), float(x.significance) if x.significance else 0.0)
    )

    # template_path = str(TEMPLATE_DIR / f"{template_name}.jinja2")
    env = Environment(loader=FileSystemLoader(searchpath=str(TEMPLATE_DIR)), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(f"{template_name}.jinja2")
    stream.write(template.render(entries=entries))
