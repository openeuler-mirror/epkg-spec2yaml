import sys
sys.path.append("../")
from actions.writer.spec_writer import *
test_spec_writer = SpecWriter(yaml_fpath="test_yaml.yaml", shell_fpath="test_shell.sh", conf_fpath="test_conf.conf")


def test_run_get_tab_str(test_str="    this is a test paragraph"):
    result = get_tab_str(test_str)
    if result == "":
        raise Exception("can't get tab str")


def test_run_combine_if_lines(test_str="%ifarch x86_64 \n...\n%ifarch x86_64\n...\n%endif\n"):
    result = combine_if_lines(test_str)
    if len(re.findall("%if", result)) >= 2:
        raise Exception("fail to combine 'if' lines")


def test_run_parse():
    try:
        test_spec_writer.parse()
    except Exception:
        raise Exception("run parse failed")


def test_run_parse_files():
    if 'files' in test_spec_writer.extra['content']:
        try:
            files = copy.deepcopy(test_spec_writer.extra['content']['files'])
            test_spec_writer.parse_files(files)
        except Exception:
            raise Exception("fail to parse files")
    else:
        logger.warn("this case needn't be test")


def test_run_read_configures_file():
    try:
        test_spec_writer.read_configures_file(test_spec_writer.conf_fpath)
    except Exception:
        raise Exception("can't read configure file")


def test_run_iterate_keys_sub():
    try:
        shell_content_f = open(change_yaml2sh_file(test_spec_writer.yaml_fpath), "r")
        shell_content = shell_content_f.read()
    except IOError:
        shell_content = ""
    try:
        test_spec_writer.iterate_keys_sub(shell_content)
    except Exception:
        raise Exception("fail to run iterate_keys_sub")


def test_run_update_shell_content():
    shell_data_f = open("test_shell.sh", "r")
    shell_data = shell_data_f.read()
    test_spec_writer.metadata["build"] = ""
    try:
        test_spec_writer.update_shell_content(shell_data, "build")
    except Exception:
        raise Exception("fail to update shell content")
