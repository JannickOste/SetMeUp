import os
from os.path import exists
from sys import platform
from typing import Union

from Classes.Configuration import Configuration
import subprocess
import re


class Registry:
    __registry_id: int = -1

    def __getInstallWindows(self, program_name: str):
        """
            Get installation path from registry on windows (CURRENTLY ONLY TESTED ON x64)
            :param program_name:
            :return:
        """
        # TODO: Check x86 registration compatibility
        from winreg import ConnectRegistry, HKEY_LOCAL_MACHINE, EnumKey, OpenKey, QueryValueEx, EnumValue

        if self.__registry_id == -1:
            self.__registry_id = HKEY_LOCAL_MACHINE

        fetcher, value_id = Configuration.getRegistryKey(program_name)
        registry = ConnectRegistry(None, self.__registry_id)

        path = ""

        if isinstance(fetcher, tuple):
            fetcher = [fetcher]

        out = None
        try:
            if isinstance(fetcher, str):
                out = EnumValue(OpenKey(registry, fetcher), 0)
            elif isinstance(fetcher, list):
                for slice in fetcher:
                    slice = tuple(slice) if isinstance(slice, list) else slice

                    if isinstance(slice, str):
                        path += f"\\{slice}"
                        continue
                    elif isinstance(slice, tuple) and len(slice) == 2:
                        reg_key, slice_id = slice
                        path += ('\\' if path != '' else '')
                        path += reg_key

                        if isinstance(slice_id, int):

                            if slice != fetcher[-1]:

                                path += f"\\{EnumKey(OpenKey(registry, path), slice_id)}"
                            else:
                                out = EnumKey(OpenKey(registry, path), slice_id)
                        elif isinstance(slice_id, str):
                            if slice != tuple(fetcher[-1]):
                                path += f"\\{QueryValueEx(OpenKey(registry, path), slice_id)}"
                            else:
                                out = QueryValueEx(OpenKey(registry, path), slice_id)
        finally:
            if out is not None:
                return out[value_id]

    def __getInstallLinux(self, program_name: str) -> str:
        """
            Private: Get installation path for application on linux

            :param program_name: program you want to locate
            :return: installation path / None
        """
        # todo: ADD VERSION CHECK DEBIAN/ETC..
        # Static method suppressor
        _ = self

        if program_name == "chrome" and not platform == "win32":
            program_name = "chromium"
        print(program_name)
        loc = subprocess.getoutput(f"which {program_name}")
        return loc

    def getInstallLocation(self, program_name: str):
        """
            Public: Get installation path (os transparent)

            :param program_name: program name you wish to locate
            :return:
        """
        # TODO: Add some kind of basic mac support (gotta look into hackintosh no mac here)
        if platform == "win32":
            return self.__getInstallWindows(program_name)
        elif platform == "linux":
            return self.__getInstallLinux(program_name)
