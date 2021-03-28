from os import listdir
from os.path import join, exists

import requests

from Browser.Exceptions import BrowserNotSupported
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

    """
        def downloadAddons(self, addon_uris: list) -> None:

        driver_name = self.__driver_conf.get("executable_name")
        for addon_uri in addon_uris:
            web: bool = any([addon_uri.startswith(prefix) for prefix in ["http", "https", "www"]])

            if not web:
                continue

            uri = None
            if driver_name == "firefox":
                self.goto(addon_uri)
                self.__download(self.__target_driver.find_element(By.LINK_TEXT, "Add to Firefox").get_attribute("href"))
            elif driver_name == "chrome":
                # Download CRX
                self.goto("https://crxextractor.com/")
                self.__target_driver.find_element(By.CLASS_NAME, "button-primary").click()

                sleep(1)

                self.__target_driver.find_element(By.CSS_SELECTOR, "#crx-download-input").send_keys(addon_uri)
                self.__target_driver.find_element(By.CSS_SELECTOR, ".download-crx-ok").click()
                addon_uri = self.__target_driver.find_element(By.CSS_SELECTOR, ".download-crx").get_attribute("href")
                self.__convertChromeExtension(self.__download(addon_uri))


    """
    def downloadAddons(self, addon_uris: list) -> None:
        raise NotImplementedError

    """
        def installAddons(self, on_bot: bool = False):
        driver_name = self.__driver_conf.get("executable_name")
        download_path = Configuration.getBrowserConfiguration("download_path")
        downloads = listdir(download_path)

        if not on_bot:
            self.release()

        for file in [file for file in downloads if file.lower().endswith(self.__getExtensionPrefix(True))]:
            extension_path = os.path.join(Configuration.getBrowserConfiguration("download_path"), file)

            if driver_name == "firefox":
                Shell.run(self.__binary_path, f'"{extension_path}"')
                sleep(2)
                for i in range(0, 4):
                    loc = (0, 0)
                    attempts = 0
                    while loc == (0, 0) and attempts < 5:
                        loc = self.__locateBoxOnScreen(rgb_color=(0, 96, 223), min_area=(175, 30))
                        attempts+= 1
                    if loc != (0, 0):
                        pyautogui.click(loc[0], loc[1])
            elif driver_name == "chrome":
                file_name = extension_path.replace("\\", "/").split("/")[-1].split(".")[0]
                extract_path = os.path.join(download_path, file_name)
                if not os.path.exists(extract_path):
                    with zipfile.ZipFile(extension_path, "r") as zip_obj:
                        zip_obj.extractall(extract_path)

                subprocess.call([self.__binary_path, f'--load-extension="{extract_path}"'])

        if self.__target_driver is not None:
            self.start()
    """
    def installAddons(self, on_bot: bool = False):
        raise NotImplementedError

    """
        Default methods
    """

    def goto(self, uri):
        self._bot.driver.get(uri)

    def download(self, uri: str) -> str:
        request = requests.get(uri, allow_redirects=True)
        if request.status_code == 200:
            file_name = uri.split('/')[-1]
            file_path = join(Configuration.getBrowserConfiguration("download_path"), file_name)

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
                    print(self._bot.downloads)
                else:
                    print(f"[Failed to write file]: {file_name} to {file_path}")

                return file_path

    def _getExtensionPrefix(self, extracted = False):
        from Browser.Actions.FirefoxActions import FirefoxActions
        from Browser.Actions.ChromeActions import ChromeActions

        if issubclass(self.__class__, FirefoxActions):
            return "xpi"
        elif issubclass(self.__class__, ChromeActions):
            return "zip" if extracted else "crx"
        else:
            raise BrowserNotSupported.BrowerNotSupported(f"No prefix found for "
                                                         f"{self.__class__.__name__.replace('Actions', '')}")
