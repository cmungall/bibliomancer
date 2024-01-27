from typing import TypedDict, Collection


class Entry(TypedDict):
    title: str
    year: int
    authors: Collection["Author"]


class Author(TypedDict):
    name: str
    orcid: str
