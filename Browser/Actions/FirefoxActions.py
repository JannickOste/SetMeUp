from abc import ABC
from os import listdir
from os.path import join
from time import sleep

from pyautogui import click
from selenium.webdriver.common.by import By

from Browser.Actions.IActions import IActions
from Classes.Shell import Shell


class FirefoxActions(IActions, ABC):
    def __init__(self, bot):
        super().__init__(bot)

    def downloadAddons(self, addon_uris: list) -> None:
        for addon_uri in addon_uris:
            web: bool = any([addon_uri.startswith(prefix) for prefix in ["http", "https", "www"]])

            if not web:
                continue

            self.goto(addon_uri)
            self.download(self._bot.driver.find_element(By.LINK_TEXT, "Add to Firefox").get_attribute("href"))

    def installAddons(self, on_bot: bool = False, addon_paths: list = None):
        download_path = self._bot.getConfig("download_path")
        downloads = listdir(download_path)

        if not on_bot:
            self._bot.release()

        addon_paths = addon_paths if addon_paths is not None else [file for file in downloads if file.lower().endswith(self._getExtensionPrefix(True))]
        for file in addon_paths:
            extension_path = join(download_path, file)

            Shell.run(self._bot.getConfig("executable_path"), f'"{extension_path}"')
            sleep(2)
            for i in range(0, 4):
                loc = (0, 0)
                attempts = 0
                while loc == (0, 0) and attempts < 5:
                    loc = self._bot.locateBoxOnScreen(rgb_color=(0, 96, 223), min_area=(175, 30))
                    attempts += 1
                if loc != (0, 0):
                    click(loc[0], loc[1])
