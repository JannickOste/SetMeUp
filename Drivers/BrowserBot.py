import shutil, zipfile
import subprocess
from os import listdir
from os.path import join
from time import sleep

import cv2
import numpy
import pyautogui
from PIL import Image
from selenium.webdriver import DesiredCapabilities
import selenium
import os
import requests

from selenium.webdriver.common.by import By

from Classes.Configuration import Configuration
from Classes.Shell import Shell


class BrowserBot:
    __browser_drivers = \
        {
            "firefox": selenium.webdriver.Firefox,
            "chrome": selenium.webdriver.Chrome,
            "edge": selenium.webdriver.Edge,
            "iexplore": selenium.webdriver.Ie
        }

    __binary_path = None

    __target_driver: selenium.webdriver = None
    __driver_conf: dict = {}

    def __init__(self, browser_exec: str):
        assert browser_exec is None or os.path.exists(browser_exec)

        self.__binary_path = browser_exec

        driver_name = browser_exec.split("\\")[-1]
        self.__driver_conf = {
            "selenium_driver": self.__browser_drivers.get(driver_name),
            "binary": browser_exec,
            "executable_name": driver_name.split(".")[0],
            "executable_file": driver_name,
            "executable_path": Configuration.getDriverPath(driver_name=driver_name.split(".")[0])
        }

    def start(self):
        driver = self.__browser_drivers.get(self.__driver_conf.get("executable_name"))
        self.__target_driver = driver(**self.__getProfile(driver), executable_path=self.__driver_conf["executable_path"])
        self.__target_driver.maximize_window()


    def __getProfile(self, driver: selenium.webdriver):
        """
        Fetch driver specific profile
        :param driver:
        :return:
        """
        profile: dict = {}
        if isinstance(driver, selenium.webdriver.Firefox):
            profile = {"firefox_options" : selenium.webdriver.FirefoxProfile()}
            profile["firefox_options"].set_preference("browser.download.folderList", 2)
            profile["firefox_options"].set_preference("browser.download.dir", Configuration.getBrowserConfiguration("download_path"))
            profile["firefox_options"].set_preference("browser.download.manager.showWhenStarting", False)
            profile["firefox_options"].set_preference("browser.helperApps.neverAsk.saveToDisk", "*")
        elif isinstance(driver, selenium.webdriver.Chrome):
            profile = {"chrome_options" : selenium.webdriver.ChromeOptions()}
            profile["chrome_options"].add_experimental_option("prefs", {
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "download.default_directory": Configuration.getBrowserConfiguration("download_path")
            })
        elif isinstance(driver, selenium.webdriver.Ie):
            profile =  {"ie_options" : selenium.webdriver.IeOptions()}

        return profile

    def __getCapabilities(self, driver: selenium.webdriver):
        capabilities = DesiredCapabilities()
        if isinstance(driver, selenium.webdriver.Firefox):
            capabilities = capabilities.FIREFOX.copy()
        elif isinstance(driver, selenium.webdriver.Chrome):
            capabilities = capabilities.CHROME.copy()
        elif isinstance(driver, selenium.webdriver.Ie):
            capabilities = capabilities.INTERNETEXPLORER.copy()
        elif isinstance(driver, selenium.webdriver.Edge):
            capabilities = capabilities.EDGE.copy()

        return capabilities

    def __getExtensionPrefix(self, extracted: bool = False) -> str:
        driver_name = self.__driver_conf.get("executable_name")

        if driver_name == "chrome":
            return "zip" if extracted else "crx"
        elif driver_name == "firefox":
            return "xpi"
        else:
            raise Exception("Browser not supported")

    def goto(self, uri):
        self.__target_driver.get(uri)

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

    def __download(self, uri: str) -> str:
        request = requests.get(uri, allow_redirects=True)
        if request.status_code == 200:
            file_name = uri.split('/')[-1]
            file_path = join(Configuration.getBrowserConfiguration("download_path"), file_name)

            try:
                open(file_path, "wb").write(request.content)
            except OSError:
                extension = self.__getExtensionPrefix()
                file_name = f"{len(listdir(Configuration.getBrowserConfiguration('download_path')))}.{extension}"
                file_path = join(Configuration.getBrowserConfiguration("download_path"), file_name)

                open(file_path, "wb").write(request.content)
            finally:
                if os.path.exists(file_path):
                    print(f"[Wrote file]: {file_name} to {file_path}")
                else:
                    print(f"[Failed to write file]: {file_name} to {file_path}")
                return file_path

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

    def __locateBoxOnScreen(self, rgb_color, min_area):
        search_box = numpy.asarray(Image.new("RGB", min_area, color=rgb_color))
        desktop_image = numpy.asarray(pyautogui.screenshot())

        result = cv2.matchTemplate(desktop_image, search_box, cv2.TM_SQDIFF_NORMED)

        return cv2.minMaxLoc(result)[2]


    def __convertChromeExtension(self, file_path):
        self.goto("https://crxextractor.com/")
        self.__target_driver.find_element(By.CLASS_NAME, "button-primary").click()
        sleep(1)
        self.__target_driver.find_element(By.ID, "file").send_keys(file_path)
        sleep(1)
        # cannot get href -> blob (browser specific data)
        self.__target_driver.find_element(By.CLASS_NAME, "download").click()

        # Temporary fix for chrome not setting download directory correctly
        # TODO: look into^
        file_name = file_path.replace("\\", "/").split("/")[-1].split('.')[0]
        while not os.path.exists(os.path.join(os.environ['USERPROFILE'], "Downloads", f"{file_name}.zip")):
            sleep(0.1)

        shutil.move(os.path.join(os.environ['USERPROFILE'], "Downloads", f"{file_name}.zip"),
                    os.path.join(Configuration.getBrowserConfiguration("download_path"), f"{file_name}.zip"))

        os.remove(file_path)

    def release(self):
        if self.__target_driver is not None:
            self.__target_driver.quit()
