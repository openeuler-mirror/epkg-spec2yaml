class ToolChainCmakeTemplate:
    def __init__(self, **kwargs):
        self.sysroot_path = kwargs["sysroot_path"] if "sysroot_path" in kwargs.keys() else\
            "/root/openeuler_gcc_arm64le/sysroot/"
        self.cross_gnu_path = kwargs["cross_gnu_path"] if "cross_gnu_path" in kwargs.keys() else\
            "/root/openeuler_gcc_arm64le/aarch64-openeuler-linux-gnu/"
        self.system_gcc_path = kwargs["system_gcc_path"] if "system_gcc_path" in kwargs.keys() else "/usr/bin/"
        self.adding_order = ""
        self.base_text = 'cat > /root/rpmbuild/BUILD/toolchain.cmake << EOF\n\
set( CMAKE_SYSTEM_NAME "Linux" )\n\
set( CMAKE_C_COMPILER "/root/openeuler_gcc_arm64le/bin/aarch64-openeuler-linux-gnu-gcc" )\n\
set( CMAKE_CXX_COMPILER "/root/openeuler_gcc_arm64le/bin/aarch64-openeuler-linux-gnu-g++" )\n\
set( CMAKE_INCLUDE_PATH {0}usr/include )\n\
{3}\n\
EOF\n'
        self.toolchain_option = "\nexport TOOLCHAIN_CONFIG=-DCMAKE_TOOLCHAIN_FILE=../" \
                                "toolchain.cmake\n"

    def add_set_order(self, cmake_set_orders: list):
        """
        增加set命令
        :param cmake_set_orders:
        :return:
        """
        for order_dict in cmake_set_orders:
            if type(order_dict) != dict:
                return
            else:
                for item_key, item_value in order_dict.items():
                    if item_key == "sysroot_path":
                        self.sysroot_path = item_value
                    elif item_key == "cross_gnu_path":
                        self.cross_gnu_path = item_value
                    elif item_key == "system_gcc_path":
                        self.system_gcc_path = item_value
                    else:
                        self.adding_order += "set( " + item_key + " " + item_value + " )\n"

    def get_final_context(self, target_type="spec"):
        """
        返回格式化后的cmake文件内容
        :param target_type:
        :return:
        """
        if target_type == "spec":
            return self.toolchain_option + self.base_text.format(self.sysroot_path, self.cross_gnu_path,
                                                                 self.system_gcc_path, self.adding_order)
        return self.base_text.format(self.sysroot_path, self.cross_gnu_path, self.system_gcc_path, self.adding_order)
