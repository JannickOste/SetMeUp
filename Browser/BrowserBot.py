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

from Browser.Actions.ChromeActions import ChromeActions
from Browser.Actions.FirefoxActions import FirefoxActions
from Browser.Actions.IActions import IActions
from Classes.Configuration import Configuration
from Classes.Shell import Shell


class BrowserBot:
    action: IActions = None
    driver: selenium.webdriver = None

    __driver_conf: dict = {}
    __browser_drivers = \
        {
            "firefox": selenium.webdriver.Firefox,
            "chrome": selenium.webdriver.Chrome,
            "edge": selenium.webdriver.Edge,
            "iexplore": selenium.webdriver.Ie
        }
    __downloads: dict = {}

    @property
    def downloads(self):
        return self.__downloads

    @downloads.setter
    def downloads(self, val):
        self.__downloads = dict(**self.__downloads, **val)

    def __init__(self, browser_exec: str):
        assert browser_exec is None or os.path.exists(browser_exec)

        driver_name = browser_exec.split("\\")[-1]
        self.__driver_conf = {
            "selenium_driver": self.__browser_drivers.get(driver_name),
            "binary": browser_exec,
            "executable_name": driver_name.split(".")[0],
            "executable_file": driver_name,
            "executable_path": Configuration.getDriverPath(driver_name=driver_name.split(".")[0]),
            **Configuration.getBrowserConfiguration("")
        }

    def start(self):
        driver = self.__browser_drivers.get(self.__driver_conf.get("executable_name"))
        self.driver = driver(**self.__getProfile(driver), executable_path=self.__driver_conf["executable_path"])
        self.driver.maximize_window()

        self.action = self.__getActions(self.driver)

    def getConfig(self, config_name):
        return self.__driver_conf.get(config_name)

    def __getActions(self, driver: selenium.webdriver) -> IActions:
        if isinstance(driver, selenium.webdriver.Firefox):
            return FirefoxActions(self)
        elif isinstance(driver, selenium.webdriver.Chrome):
            return ChromeActions(self)

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


    def release(self):
        if self.driver is not None:
            self.driver.quit()
