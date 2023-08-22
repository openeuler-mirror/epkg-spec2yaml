#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
功能：提供统一错误码协议规范和格式，交互标准化，用于快速定位
错误码规则：

错误阶段：用于应用标识，由一位字母表示， C=compile, P=package,D=deploy,U=unit test ,S=system integration test
错误归属：用于责任标识，由一位数字表示， 1=业务代码逻辑问题，2=工程类脚本与配置类问题

错误类型：用于错误分类，
错误编码：
版权信息：Copyright Huawei Technologies Co., Ltd. 2010-2022. All rights reserved.
"""
EXCEPTION_STAGE = {
    'C': 'Acton: compile\n',
    'P': 'Acton: package\n',
    'D': 'Acton: deploy\n',
    'U': 'Acton: unit test\n',
    'S': 'Acton: system integration test\n'
}
EXCEPTION_RESPONSE = {
    1: "Responsibility: business code logic issues\n",
    2: "Responsibility: engineering script and configuration problems\n"
}
EXCEPTION_CODE = {
    # 4xx 系统环境类, 子类别由第二位数字控制
    400: 'ERROR_Code=400,Environment verification: The operating system version is inconsistent. The system '
         'environment specified by YAML cannot be found.',
    401: 'ERROR_Code=401,Environment verification: The environment hardware configuration does not meet the minimum '
         'configuration specified by YAML.',
    402: 'ERROR_Code=402,Environment verification: The version of the installed tool is inconsistent with that '
         'specified by YAML.',
    403: 'ERROR_Code=403,Environment verification: The tool is not installed.',

    410: 'ERROR_Code=410,Environment running: Downloading Docker Image timed out.',
    411: 'ERROR_Code=411,Environment running: Failed to run Docker Container.',
    412: 'ERROR_Code=412,Environment running: Failed to mount the data volume.',
    413: 'ERROR_Code=413,Environment running: file system I/O conflict!',
    414: 'ERROR_Code=414,Environment running: The system crashes.',

    420: 'ERROR_Code=420,Environment running: The file does not exist.',
    421: 'ERROR_Code=421,Failed to open the file.'
         ' Check whether the configured file format is consistent with the actual file format.',
    422: 'ERROR_Code=422,Failed to copy the file. Please check whether the source file exists.',
    423: 'ERROR_Code=423,Failed to modify the file content. The sed does not take effect. '
         'Check whether the configuration for modifying the file content is correct.',

    # 5xx 依赖管理类, 子类别由第二位数字控制
    500: 'ERROR_Code=500, binary dependency download: The configuration file for dependency definition cannot be '
         'found.',
    501: 'ERROR_Code=501, binary dependency download: The dependency package download source cannot be found.',
    502: 'ERROR_Code=502, binary dependency download: An error occurred when parsing the dependency configuration '
         'file format.',

    510: 'ERROR_Code=510,Maven dependency download: The configuration file of the dependency definition cannot be '
         'found.',
    511: 'ERROR_Code=511,Maven dependency download: The dependency package download source cannot be found.',
    512: 'ERROR_Code=512,Maven dependency download: An error occurred when parsing the dependency configuration file '
         'format.',

    520: 'ERROR_Code=520,Go Dependency Download: The configuration file of the dependency definition cannot be found.',
    521: 'ERROR_Code=521,Go Dependency Download: The dependency package download source cannot be found.',
    522: 'ERROR_Code=522,Go Dependency Download: An error occurred when parsing the dependency configuration file '
         'format.',

    530: 'ERROR_Code=530,NPM Dependency Download: The configuration file for dependency definition cannot be found.',
    531: 'ERROR_Code=531,NPM Dependency Download: The dependency package download source cannot be found.',
    532: 'ERROR_Code=532,NPM Dependency Download: An error occurred when parsing the dependency configuration file '
         'format.',

    540: 'ERROR_Code=540,Pypi Dependency Download: The configuration file of the dependency definition cannot be'
         ' found.',
    541: 'ERROR_Code=541,Pypi Dependency Download: The dependency package download source cannot be found.',
    542: 'ERROR_Code=542,Pypi Dependency Download: An error occurred when parsing the dependency configuration file '
         'format.',

    550: 'ERROR_Code=550,Source code download: invalid remote repository!',
    551: 'ERROR_Code=551,Source code download: remote repository time out!',
    552: 'ERROR_Code=552,Source code download: Git pull remote and local cache conflict!',
    553: 'ERROR_Code=553,Source code check: Invalid local code repository.',

    560: 'ERROR_Code=560,Dependency parsing: Failed to execute the dependency parsing command.',
    561: 'ERROR_Code=561,Dependency analysis: Failed to export the dependency analysis report.',
    562: 'ERROR_Code=562,Dependency analysis: Cyclic dependency exists.',

    # 6xx 操作类，子类别由第二位数字控制
    600: 'ERROR_Code=600,Configuration file: The file does not exist.',
    601: 'ERROR_Code=601,Configuration file: Failed to parse the configuration file. Please check the format.',
    602: 'ERROR_Code=602,Configuration file: Failed to parse parameters.',

    610: 'ERROR_Code=610,Command execution class: Failed to execute the command.'
         ' Check whether the command is correct or whether the code is incorrect.',

    620: 'ERROR_Code=620,Encryption and decryption: The public and private key certificates cannot be found.',
    621: 'ERROR_Code=621,Encryption and decryption: Failed to execute the encryption and decryption tool.',

    630: 'ERROR_Code=630,File operation: Failed to rename or move the file. '
         'Please check the path, repeatability, and permission.',
    631: 'ERROR_Code=631,File operation: Failed to set the file permission chmod.'
         ' Please check the operation permission.',
    632: 'ERROR_Code=632,File operation: Failed to copy the file. Check whether the path and permission are correct.',
    633: 'ERROR_Code=633,File operation: Failed to set the file hyperlink. '
         'Please check whether the path and permission are correct.',
    634: 'ERROR_Code=634,File operation: Failed to decompress the package.',
    635: 'ERROR_Code=634,File operation: Failed to compress the file.',
}
