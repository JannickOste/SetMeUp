from os.path import exists
from sys import platform
from time import sleep

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By

from Browser.Actions.ChromeActions import ChromeActions
from Browser.Actions.FirefoxActions import FirefoxActions
from Browser.Actions.IActions import IActions

from Classes.Configuration import Configuration


class BrowserBot:
    action: IActions = None
    driver: webdriver = None

    __driver_conf: dict = {}
    __browser_drivers = \
        {
            "firefox": webdriver.Firefox,
            "chrome" if platform == "win32" else "chromium": webdriver.Chrome,
            "edge": webdriver.Edge,
            "iexplore": webdriver.Ie
        }

    __downloads: dict = {}

    def __init__(self, browser_exec: str):
        if platform == "win32":
            assert browser_exec is None or exists(browser_exec)

        driver_name = browser_exec.split("\\" if platform == "win32" else "/")[-1]
        self.__driver_conf = {
            "selenium_driver": self.__browser_drivers.get(driver_name),
            "binary": browser_exec,
            "executable_name": driver_name.split(".")[0],
            "executable_file": driver_name,
            "executable_path": Configuration.getDriverPath(
                                driver_name="chrome" if platform != "win32" and driver_name == "chromium" else
                                driver_name.split(".")[0]
                                ),
            **Configuration.getBrowserConfiguration("")
        }

    """
        Public methods.
    """

    def start(self):
        driver = self.__browser_drivers.get(self.__driver_conf.get("executable_name"))
        self.driver = driver(**self.__getProfile(driver), executable_path=self.__driver_conf["executable_path"])

        self.driver.maximize_window()

        print(f"[LAUNCHING_AGENT]: {self.driver.name}")
        self.action = self.__getActions(self.driver)

    def getConfig(self, config_name):
        """
            Get driver configuration
            :param config_name: config_key
            :return:
        """
        assert config_name in self.__driver_conf.keys()

        return self.__driver_conf.get(config_name)

    def release(self, clear_downloads: bool = False) -> None:
        """
            Release the driver if driver has been initiated
            :param clear_downloads: clear session downloads dictionary
            :return:
        """

        if self.driver is not None:
            while self.downloadsActive():
                print(f"[RELEASE_DELAY::{self.__driver_conf['executable_name']}]: still downloading")
                sleep(5)

            self.driver.quit()
            print(f"[RELEASING AGENT]: {self.__driver_conf['executable_name']}")
        if clear_downloads:
            self.__downloads.clear()

    """
        Properties
    """

    @property
    def downloads(self):
        """
        Fetch downloaded files in session.
        :return:
        """
        return self.__downloads

    @downloads.setter
    def downloads(self, val):
        #  todo: add file check

        self.__downloads = dict(**self.__downloads, **val)

    def downloadsActive(self) -> bool:
        self.driver.get("chrome://downloads/")

        manager = self.driver.find_element(By.TAG_NAME, "downloads-manager")
        return any([text in manager.text.lower() for text in ["pause", "cancel"]])


    def __getProfile(self, driver: webdriver):
        """
        Fetch driver specific profile
        :param driver:
        :return:
        """
        # todo: preferences not applying (why ? )
        profile: dict = {}
        if issubclass(driver, webdriver.Firefox):
            ff_profile = webdriver.FirefoxProfile()

            ff_profile.set_preference("browser.download.folderList", 2)
            ff_profile.set_preference("browser.download.dir", self.getConfig("download_path"))
            ff_profile.set_preference("browser.helperApps.alwaysAsk.force", False)
            ff_profile.set_preference("browser.download.manager.showWhenStarting", False)
            ff_profile.set_preference("browser.download.manager.focusWhenStarting", False)
            ff_profile.set_preference("browser.download.manager.useWindow", False)
            ff_profile.set_preference("browser.download.manager.showAlertOnComplete", False)
            ff_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-msdownload")
            ff_profile.binary = self.__driver_conf["binary"]

            profile["firefox_options"] = webdriver.FirefoxOptions()
            profile["firefox_options"].profile = ff_profile
        elif issubclass(driver, webdriver.Chrome):

            profile = {"chrome_options": webdriver.ChromeOptions()}
            profile["chrome_options"].add_experimental_option("prefs", {
                'safebrowsing.enabled': True,
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "download.default_directory": f'{Configuration.getBrowserConfiguration("download_path")}/'
            })
            print(profile)
            print(self.getConfig("download_path"))
        elif issubclass(driver, webdriver.Ie):
            profile = {"ie_options": webdriver.IeOptions()}
        print(profile)
        return profile

    def __getCapabilities(self, driver: webdriver):
        """
            Get default browser capabilities
            :param driver:
            :return:
        """
        # Suppressor for method may be static
        _ = self

        capabilities = DesiredCapabilities()
        if isinstance(driver, webdriver.Firefox):
            capabilities = capabilities.FIREFOX.copy()
        elif isinstance(driver, webdriver.Chrome):
            capabilities = capabilities.CHROME.copy()
        elif isinstance(driver, webdriver.Ie):
            capabilities = capabilities.INTERNETEXPLORER.copy()
        elif isinstance(driver, webdriver.Edge):
            capabilities = capabilities.EDGE.copy()

        return capabilities

    def __getActions(self, driver: webdriver) -> IActions:
        """
            Get IActions interface for browser

            :param driver:
            :return:
        """
        if isinstance(driver, webdriver.Firefox):
            return FirefoxActions(self)
        elif isinstance(driver, webdriver.Chrome):
            return ChromeActions(self)
