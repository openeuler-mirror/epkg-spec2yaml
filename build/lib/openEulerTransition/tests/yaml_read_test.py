import sys
sys.path.append("../")
from openEulerTransition.actions.writer.yaml_writer import *
test_spec_parser = SpecParser()


def test_run_read():
    try:
        test_spec_parser.read("test_spec.spec")
    except Exception:
        raise Exception("fail to read test spec file")


def test_run_find_quotes_from_words():
    try:
        find_quotes_from_words("")
    except Exception:
        raise Exception("fail to run function find_quotes_from_words")


def test_run_collation_original_data():
    try:
        test_spec_parser.collation_original_data(test_spec_parser.items)
    except Exception:
        raise Exception("fail to collation original data")


def test_run_divide_into_shell():
    try:
        value = test_spec_parser.items["build"]
        test_spec_parser.divide_into_shell("build", value)
    except Exception:
        raise Exception("fail to divide into shell")


def test_run_cooked_items():
    try:
        test_spec_parser.cooked_items()
    except Exception:
        raise Exception("fail to cook items")
