import re
from os.path import dirname, join, abspath
from sys import platform
import json


class Configuration:
    __assetPath = "Assets"
    __config_name = "Configuration.json"
    __config: dict = {}

    @classmethod
    def __init__(cls):
        """
        Load JSON file: {__assetsPath} / {__config_name}
        """
        cls.__config = cls.__parseConfiguration()

    @classmethod
    def __parseConfiguration(cls) -> dict:
        def replace_value(obj, search_value, rep_value):
            for k, v in obj.items():
                if isinstance(v, dict):
                    obj[k] = replace_value(v, search_value, rep_value)
                elif isinstance(v, str):
                    obj[k] = re.sub(r"/" if platform == "win32" else r"\\", r"\\" if platform == "win32" else r"/",
                                    v.replace(search_value, rep_value))

            return obj

        root = json.loads(open(cls.getAssetPath([cls.__config_name]), "r").read())["configuration"]
        for search_key, replace_key in [("{ASSETS}", cls.getAssetPath())]:
            root.update(replace_value(root, search_key, replace_key))

        root.update(json.loads(open(cls.getAssetPath(["Extensions.json"]), "r").read()))
        print(root)
        return root

    @classmethod
    def getAssetPath(cls, suffix: list = None):
        """
        Get base asset path
        :param suffix: additions to base path
        :return: base path (+ additions)
        """
        suffix = suffix if suffix is not None else []

        # Is Windows path, is linux path
        if re.search(r"(?=^[A-Za-z]+:\\.*|^\\.*|^/.*)", cls.__assetPath) is None:
            directory = dirname(dirname(abspath(__file__)))
            cls.__assetPath = join(directory, cls.__assetPath)

        return join(cls.__assetPath, *suffix)

    @classmethod
    def getDriverPath(cls, driver_name):
        """
        Get browser driver module
        :param driver_name: driver name
        :return: path to driver binary
        """
        driver_conf: dict = cls.__config.get("drivers")
        print(driver_name)
        if driver_conf is not None:
            assert all([key in driver_conf.keys() for key in (["suffix", driver_name] if platform == "win32"
                                                              else [driver_name])])

            driver_path = driver_conf.get(driver_name).get(platform)

            return cls.getAssetPath([driver_conf.get("suffix"), platform, driver_path])

    @classmethod
    def getRegistryKey(cls, program_name: str):
        """
        Get windows registration key
        :param program_name: name of the program
        :return: registration bindings for access
        """
        registry_conf: dict = cls.__config.get("registry")
        if registry_conf is not None:
            assert program_name in registry_conf.keys()

            return tuple(registry_conf.get(program_name))

    @classmethod
    def getBrowserConfiguration(cls, config_key: str):
        """
        :param config_key:
        :return:
        """
        browser_conf: dict = cls.__config.get("browser")
        if browser_conf is not None:
            if config_key is None or len(config_key) == 0:
                return browser_conf

            assert config_key in browser_conf.keys()

            result = browser_conf.get(config_key)
            return result if "{ASSETS}" not in result else result.format(ASSETS=cls.getAssetPath())

    @classmethod
    def getExtensions(cls, brower_name: str):
        extension_conf: dict = cls.__config.get("extensions")
        if extension_conf is not None:
            if brower_name is None or not len(brower_name):
                return extension_conf

            assert brower_name in extension_conf.keys()
            return extension_conf.get(brower_name)
