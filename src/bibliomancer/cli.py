"""Command line interface for bibliomancer."""

import logging
import sys

import click

from bibliomancer import __version__, mergeutil, eutils

__all__ = [
    "main",
]

from bibliomancer.formatter import generate_markdown

from bibliomancer.enricher import repair_file, repair_all_iter, annotate_author_position
from bibliomancer.io import load_file_iter, write_file, load_file
from bibliomancer.datamodel.enums import BiblioSchemaEnum, BiblioSyntaxEnum
from bibliomancer.mapper import map_entries
from bibliomancer.validator import validate_entries_iter

logger = logging.getLogger(__name__)


input_option = click.option("--input", "-i", type=click.File("r"), default=sys.stdin, help="Input file")
output_option = click.option("--output", "-o", type=click.File("w"), default=sys.stdout, help="Output file")
input_format_option = click.option(
    "--input-format",
    "-f",
    type=click.Choice([e for e in BiblioSyntaxEnum]),
    # default="csv",
    help="Format of input files",
)
output_format_option = click.option(
    "--output-format",
    "-O",
    type=click.Choice([e for e in BiblioSyntaxEnum]),
    # default="csv",
    help="Format of output files",
)
source_schema_option = click.option(
    "--source-schema", "-s", type=click.Choice([e for e in BiblioSchemaEnum]), help="Source of input file"
)
target_schema_option = click.option(
    "--target-schema", "-t", type=click.Choice([e for e in BiblioSchemaEnum]), help="Source of input file"
)
template_option = click.option("--template", "-T", help="Template")
repair_option = click.option("--repair/--no-repair", default=False, show_default=True, help="Repair entries")


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """
    CLI for bibliomancer.

    :param verbose: Verbosity while running.
    :param quiet: Boolean to be quiet or verbose.
    """
    if verbose >= 2:
        logger.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(level=logging.INFO)
    else:
        logger.setLevel(level=logging.WARNING)
    if quiet:
        logger.setLevel(level=logging.ERROR)


@main.command()
@input_option
@output_option
@input_format_option
@output_format_option
def repair(input, output, **kwargs):
    """Repair a biblio file.

    Limitations: only supports Paperpile TSVs.
    """
    repair_file(input, output, **kwargs)


@main.command()
@input_option
@output_option
@input_format_option
@output_format_option
@source_schema_option
@target_schema_option
@template_option
@repair_option
@click.option("--author", "-a", multiple=True, help="Highlight authors")
@click.option(
    "--annotate-position/--no-annotate-position",
    default=False,
    show_default=True,
    help="Annotate position in the list of references",
)
def export(
    input,
    output,
    input_format,
    output_format,
    source_schema,
    target_schema,
    repair,
    template: str,
    author,
    annotate_position,
):
    """Export a biblio file.

    Exports to markdown or csv
    """
    entries = load_file_iter(input, format=input_format, schema=source_schema)
    if repair:
        entries = repair_all_iter(entries)
    if annotate_position:
        if not author:
            raise ValueError("Must provide at least one author to annotate position")
        entries = annotate_author_position(entries, author[0])
    if output_format == "markdown":
        generate_markdown(entries, stream=output, source_schema=source_schema, template_name=template, authors=author)
    else:
        write_file(entries, output, format=output_format, schema=target_schema)


@main.command()
@input_option
@output_option
@input_format_option
@source_schema_option
@target_schema_option
def validate(input, output, input_format, source_schema, target_schema):
    """Validate a biblio file.

    Limitations: only checks for duplicate entries.
    """
    entries = load_file_iter(input, format=input_format, schema=source_schema)
    n = 0
    for error in validate_entries_iter(entries, report_fields=["title"]):
        print(error, file=sys.stderr)
        n += 1
    if n:
        sys.exit(1)


@main.command()
@input_option
@output_option
@output_format_option
@input_format_option
@source_schema_option
@target_schema_option
@click.option("--merge-from", "-m", help="File to merge from")
@click.option("--columns", "-c", help="comma-separated list of columns to merge")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="Overwrite existing values")
def merge(input, output, input_format, output_format, source_schema, merge_from, target_schema, columns, **kwargs):
    """Merges columns from source into the input bibliography.

    The source bibliography must be in BIBM format.
    """
    target_entries = load_file(input, format=input_format, schema=source_schema)
    # print(f"Loaded {len(target_entries)} entries from {input}")
    source_entries = load_file(merge_from, schema=BiblioSchemaEnum.BIBM)
    # print(f"Loaded {len(source_entries)} entries from {merge_from}")
    cols = columns.split(",") if columns else None
    # print(f"Merging [kw={kwargs}]")
    mergeutil.merge_entries_from(target_entries, source_entries, cols=cols, **kwargs)
    # print(f"Writing {len(target_entries)} entries to {output}")
    write_file(target_entries, output, format=output_format, schema=target_schema)


@main.command()
@click.argument("pmids", nargs=-1)
def pmid2pmcid(pmids):
    """Converts PMID to PMCID."""
    for pmid in pmids:
        print(pmid, eutils.pmid_to_pmc(pmid))


if __name__ == "__main__":
    main()
