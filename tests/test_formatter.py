from io import StringIO

from bibliomancer.cli import main
from bibliomancer.formatter import generate_markdown
from bibliomancer.io import load_file_iter
from bibliomancer.datamodel.enums import BiblioSchemaEnum
from bibliomancer.mapper import map_entries
from tests import INPUT_DIR, OUTPUT_DIR


EXPECTED = (
    "Holmes IH, **Mungall CJ** (2017). "
    "**BioMake: a GNU make-compatible utility for declarative workflow management**."
    " In *Bioinformatics, 33(21):3502-3504"
)


def test_formatter(runner):
    """
    Tests formatting.

    :param runner:
    :return:pp
    """
    input_file = INPUT_DIR / "cjm.paperpile.csv"
    entries = load_file_iter(input_file)
    entries = list(entries)
    assert len(entries) > 1
    # write to a string as if it were a file
    stream = StringIO()
    generate_markdown(entries, stream=stream, authors=["Mungall CJ?"])
    md = stream.getvalue()
    assert EXPECTED in md, f"Not found in {md}"
