import os
from time import sleep

import requests
from os import listdir
from os.path import join, exists

from Bots.Browser.Exceptions import BrowserNotSupported
from Classes.Configuration import Configuration


class IActions:
    """
        The default interface for actions.
    """
    _bot = None

    def __init__(self, bot):
        self._bot = bot


    """
        Override methods
    """

    def downloadAddons(self, addon_uris: list) -> None:
        """
            Download extension files based on browser

            :param addon_uris:  url set to addons
        """
        raise NotImplementedError

    def installAddons(self, on_bot: bool = False, addon_paths: list = None) -> None:
        """
            (Convert)/install extension files based on browser

            :param on_bot: Install extension on bot
            :param addon_paths: filepath set to addons
        """
        raise NotImplementedError

    """
        Default methods
    """

    def goto(self, uri) -> None:
        """
            Goto a URI (override not advised)

            :param uri: URI to weblocation
        """
        self._bot.driver.get(uri)

    def download(self, uri: str) -> str:
        """
            Download a file and fetch filelocation if download was successfully completed (override not advised)

            :param uri: uri to weblocation
            :return: filepath / None
        """
        request = requests.get(uri, allow_redirects=True)
        download_path = self._bot.getConfig("download_path")
        if request.status_code == 200:
            if not os.path.exists(download_path):
                os.mkdir(download_path)

            file_name = uri.split('/')[-1]
            file_path = join(download_path, file_name)

            try:
                open(file_path, "wb").write(request.content)
            except OSError:
                extension = self._getExtensionPrefix()
                file_name = f"{len(listdir(Configuration.getBrowserConfiguration('download_path')))}.{extension}"
                file_path = join(Configuration.getBrowserConfiguration("download_path"), file_name)

                open(file_path, "wb").write(request.content)
            finally:
                if exists(file_path):
                    print(f"[Wrote file]: {file_name} to {file_path}")

                    self._bot.downloads[file_name] = file_path
                else:
                    print(f"[Failed to write file]: {file_name} to {file_path}")

                return file_path

    def downloadExecutables(self, exec_uris) -> None:
        """
            Download a set of windows executables. (override not advised)

            :param exec_uris: list of tuples with URI / download_btn_text(None for sleep)
            :return:
        """
        for uri, target in exec_uris:
            self.goto(uri)
            if target is None:
                sleep(2)

    def _getExtensionPrefix(self, converted: bool = False):
        """
            Get extension prefix of browser

            :param converted: Get converted extension
        """
        from Bots.Browser.Actions.FirefoxActions import FirefoxActions
        from Bots.Browser.Actions.ChromeActions import ChromeActions

        if issubclass(self.__class__, FirefoxActions):
            return "xpi"
        elif issubclass(self.__class__, ChromeActions):
            return "zip" if converted else "crx"
        else:
            raise BrowserNotSupported.BrowerNotSupported(f"No prefix found for "
                                                         f"{self.__class__.__name__.replace('Actions', '')}")
