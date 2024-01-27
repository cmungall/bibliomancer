from io import StringIO

import pytest

from bibliomancer.formatter import generate_markdown
from bibliomancer.io import load_file_iter, write_file
from bibliomancer.datamodel.enums import BiblioSchemaEnum, BiblioSyntaxEnum
from bibliomancer.mapper import map_entries
from tests import INPUT_DIR, OUTPUT_DIR


@pytest.mark.parametrize(
    "input_file,input_schema,input_syntax",
    [
        (INPUT_DIR / "cjm.paperpile.csv", BiblioSchemaEnum.PAPERPILE, BiblioSyntaxEnum.CSV),
    ],
)
@pytest.mark.parametrize(
    "output_schema,output_syntax",
    [
        (BiblioSchemaEnum.BIBM, BiblioSyntaxEnum.JSON),
        (BiblioSchemaEnum.BIBM, BiblioSyntaxEnum.CSV),
        (BiblioSchemaEnum.BIBM, BiblioSyntaxEnum.YAML),
    ],
)
def test_io(input_file, input_schema, input_syntax, output_schema, output_syntax):
    """
    Tests reading and writing.

    :param runner:
    :return:pp
    """
    entries = load_file_iter(input_file, schema=input_schema, format=input_syntax)
    entries = list(entries)
    assert len(entries) > 1
    generated_file = OUTPUT_DIR / f"test_io.{output_schema}.{output_syntax}"
    write_file(entries, generated_file, schema=output_schema, format=output_syntax)
    entries2 = load_file_iter(generated_file, schema=output_schema, format=output_syntax)
    entries2 = list(entries2)
    assert len(entries2) == len(entries)
