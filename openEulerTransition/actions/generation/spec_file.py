import os

from openEulerTransition.logs.log import logger
from openEulerTransition.actions.writer.spec_writer import SpecWriter
from openEulerTransition.actions.utils.file_operate import check_yaml_file, Chdir, check_conf_file


class CreateSPEC:
    """
    接口：None
    """

    def __init__(self, file_path, **kwargs):
        self.path = file_path
        self.conf_path = kwargs.get("conf_path")
        self.shell_path = kwargs.get("shell_path")
        self.python_path = kwargs.get("python_path")

    def transition(self):
        conf_abs_path = ""
        if self.conf_path:
            if not check_conf_file(self.conf_path):
                logger.error("Cannot find valid conf file")
                # return
            if os.path.isabs(self.conf_path):
                conf_abs_path = self.conf_path
            else:
                conf_abs_path = os.path.abspath(self.conf_path)

        if not check_yaml_file(self.path):
            logger.error("Cannot find valid yaml file")
            return
        # change to workspace dirctory
        directory = os.path.dirname(self.path)
        if self.path.find(os.path.sep) != -1 and directory != os.path.curdir:
            Chdir(directory).__enter__()
        file_name = os.path.basename(self.path)
        spec_writer = SpecWriter(file_name, conf_abs_path, shell_fpath=self.shell_path)
        spec_writer.parse()
        spec_writer.process(None)
