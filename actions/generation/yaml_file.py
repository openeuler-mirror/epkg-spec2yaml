from openEulerTransition.logs.log import logger
from openEulerTransition.actions.writer.yaml_writer import YamlWriter
from openEulerTransition.actions.utils.file_operate import check_spec_file


class CreateYAML:
    """
    接口：None
    """

    def __init__(self, file_path):
        self.path = file_path

    def transition(self):
        if not check_spec_file(self.path):
            logger.error("Cannot find valid spec file")
            return
        yaml_writer = YamlWriter(self.path)
        yaml_writer.parse()
