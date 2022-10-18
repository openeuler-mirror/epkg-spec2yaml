import os
import subprocess
import requests
from openEulerTransition.logs.log import logger
from openEulerTransition.configure.common import *


def check_environment():
    return os.uname()


def check_package_exist(package_name):
    """
    检查包是否已安装
    :param package_name:
    :return:
    """
    return package_name


def check_tool():
    """
    检查下载工具，当前仅检查wget和curl
    :return:
    """
    wget_tool = subprocess.Popen("wget --version", shell=True, close_fds=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wget_stdout, wget_stderr = wget_tool.communicate()
    wget_tool.poll()
    print(wget_stdout)
    if wget_tool.poll() == 0:
        return "wget "
    return "requests"


class DownloadWorker:
    """
    接口：下载工具
    """
    def __init__(self, name=None, package=None, url=None):
        self.build_direction = os.getcwd()
        self.download_direction = "/root/rpmbuild/SOURCES"
        self.target_warehouse = STOREHOUSE_URL + "sources_and_patches/"
        self.name = name
        self.package = package
        self.url = url

    def __check_url__(self):
        if self.url:
            result = requests.get(self.url, timeout=5)
            status = result.status_code == 200
            return status

    def __check_proxy__(self):
        logger.info(self.url)
        return True

    def download_from_warehouse(self, file_name=""):
        """
        从仓库中下载包
        :param file_name: 仓库中的文件名
        :return: 下载命令的返回状态
        """
        if file_name == "":
            file_name = self.name
        if self.download_direction:
            os.chdir(self.download_direction)
        cmd_tool = check_tool()
        if "requests" in cmd_tool:
            r = requests.get(self.target_warehouse + "/" + file_name)
            return r.status_code
        p = subprocess.Popen(cmd_tool + self.target_warehouse + "/" + file_name, shell=True, close_fds=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print(stdout)
        p.poll()
        return p.returncode

    def download_from_web(self, url=""):
        """
        网上下载
        :param url: 文件网址
        :return: 下载命令的返回状态
        """
        if url == "":
            url = self.url
        result = requests.get(url, stream=True)
        with open(self.package, 'wb') as f:
            for chunk in result.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        f.close()
        return result.status_code

    def download(self, source: str):
        """
        下载入口
        :param source: 文件源
        :return: 是否下载成功
        """
        ret = self.__check_proxy__()
        if not ret:
            logger.warn("proxy is not access")
            return False
        ret = self.__check_url__()
        if not ret:
            logger.info("url can not use")
            return False
        file_name = self.parse_source(source)
        try:
            if source.startswith("file://"):
                self.download_from_warehouse(file_name)
                os.chdir(self.build_direction)
                return True
            elif source.startswith("http"):
                self.download_from_web(source)
            else:
                self.download_from_warehouse(file_name)
        except Exception as e:
            logger.error("can't download file %s, " % file_name, str(e))
            return False
        os.chdir(self.build_direction)

    def parse_source(self, source: str):
        """
        解析源文件是否可下载
        :param source: 文件源
        :return: 文件名
        """
        self.name = source
        if source.startswith("file://") or source.startswith("http"):
            if ";" in source:
                temp_list = source.split(";")
                source = temp_list[0]
            if os.path.sep in source:
                temp_list = source.split(os.path.sep)
                self.name = temp_list[-1]
        return self.name
