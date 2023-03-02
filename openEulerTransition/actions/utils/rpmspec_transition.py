import re
import subprocess
import os
from func_timeout import func_set_timeout
from openEulerTransition.logs.log import logger


@func_set_timeout(600)
def yum_install_rpmbuild():
    """
    yum命令安装rpm-build
    :return:
    """
    install_rpmbuild = subprocess.Popen("yum install -y rpm-build", shell=True, stdout=subprocess.PIPE)
    text = install_rpmbuild.stdout.read().decode('utf-8').strip()
    if "Complete!" in text:
        return "success"
    return "failed"


def run_rpmspec_command(origin_spec_path):
    """
    原始spec文件的路径
    :param origin_spec_path:
    :return:
    """
    spec_name = os.path.basename(origin_spec_path)
    new_spec_path = origin_spec_path.replace(spec_name, "bak_" + spec_name.replace(".spec", "1.spec"))
    ret1 = os.system("rpmspec -P {0} > {1}".format(origin_spec_path, new_spec_path))
    if ret1 != 0:
        logger.error("rpmspec command error! spec path is " + origin_spec_path)
        return False
    ret2 = os.system("rm -f {0}".format(origin_spec_path))
    if ret2 != 0:
        logger.error("remove file {0} error".format(origin_spec_path))
        return False
    ret3 = os.system("mv {0} {1}".format(new_spec_path, origin_spec_path))
    if ret3 != 0:
        logger.error("rename file {0} error".format(new_spec_path))
        return False
    with open(origin_spec_path, "w") as f:
        content = f.read()
        if "%package debuginfo" in content and "%package debugsource" in content:
            extra_content = re.findall("%package debuginfo.*%package debugsource.*debugsourcefiles.list", content)[0]
            f.write(content.replace(extra_content, ""))
        f.close()
    return True


def check_rpm_spec_command(spec_path):
    """
    检查rpmspec命令，如果没有会自动安装
    :param spec_path:
    :return:
    """
    rpm_spec_help = os.system("rpmspec --help")
    if rpm_spec_help != 0:
        try:
            install_rpmbuild = yum_install_rpmbuild()
            if install_rpmbuild == "success":
                rpmspec_result = run_rpmspec_command(spec_path)
                return rpmspec_result
        except Exception as e:
            logger.error(str(e) + ": no rpmspec command")
            return False
