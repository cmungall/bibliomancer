import pytest

from bibliomancer.cli import main
from tests import INPUT_DIR, OUTPUT_DIR


def test_help(runner):
    """
    Tests help message

    :param runner:
    :return:
    """
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "repair" in result.output


def test_cli_repair(runner):
    """
    Tests repair command

    :param runner:
    :return:
    """
    input_file = INPUT_DIR / "test.paperpile.csv"
    output_file = OUTPUT_DIR / "test.csv"
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    result = runner.invoke(main, ["repair", "-i", input_file, "-o", output_file])
    if result.exit_code != 0:
        print(result.output)
    assert result.exit_code == 0
    # test file contents
    expected_str = "10.48550/2304.02711"
    with open(output_file) as stream:
        assert expected_str in stream.read()


TEST_PAPERPILE_INPUT = INPUT_DIR / "test.paperpile.csv"
TEST_OUT_CSV = OUTPUT_DIR / "test.csv"
TEST_OUT_JSON = OUTPUT_DIR / "test.json"
TEST_OUT_MD = OUTPUT_DIR / "test.md"


@pytest.mark.parametrize(
    "command,options,arguments,passes,outpath,expected",
    [
        ("repair", ["--help"], [], True, None, "repair"),
        ("repair", ["-i", TEST_PAPERPILE_INPUT, "-o", TEST_OUT_CSV], [], True, TEST_OUT_CSV, "10.48550/2304.02711"),
        ("export", ["-i", TEST_PAPERPILE_INPUT, "-o", TEST_OUT_CSV], [], True, TEST_OUT_CSV, "Fontana T|Reese J"),
        ("export", ["-i", TEST_PAPERPILE_INPUT, "-o", TEST_OUT_JSON, "-O", "json"], [], True, TEST_OUT_JSON, "SPIRES"),
        (
            "export",
            ["-i", TEST_PAPERPILE_INPUT, "-o", TEST_OUT_MD, "-O", "markdown"],
            [],
            True,
            TEST_OUT_JSON,
            "Caufield",
        ),
        (
            "export",
            ["-i", TEST_PAPERPILE_INPUT, "-o", TEST_OUT_MD, "-O", "markdown", "--author", "Caufield J?H"],
            [],
            True,
            TEST_OUT_MD,
            "**Caufield",
        ),
    ],
)
def test_all(runner, command, options, arguments, passes, outpath, expected):
    """
    Tests multiple commands

    :param runner:
    :return:
    """
    if outpath is not None:
        outpath.parent.mkdir(exist_ok=True, parents=True)
    result = runner.invoke(main, [command] + options + arguments)
    if result.exit_code != 0:
        print(result.output)
    if not passes:
        assert result.exit_code != 0
        return
    assert result.exit_code == 0
    if outpath is None:
        output_text = result.output
    else:
        with open(outpath) as stream:
            output_text = stream.read()
    assert expected in output_text
