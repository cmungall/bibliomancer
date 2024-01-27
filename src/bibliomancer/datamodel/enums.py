from enum import Enum


class BiblioSchemaEnum(str, Enum):
    """Enumeration of supported bibliographic schemas."""

    PAPERPILE = "paperpile"
    BIBM = "bibm"
    MINIMAL = "minimal"


class BiblioSyntaxEnum(str, Enum):
    """Enumeration of supported bibliographic formats."""

    BIBTEX = "bibtex"
    CSV = "csv"
    RIS = "ris"
    MARKDOWN = "markdown"
    YAML = "yaml"
    JSON = "json"
