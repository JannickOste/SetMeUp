import os

from selenium import webdriver

from Classes.Registry import Registry
from Classes.Configuration import Configuration

from Bots.Browser.BrowserBot import BrowserBot
from Bots.Browser.Actions.IActions import IActions


class BotHandler:
    registry: Registry = None
    __agents = {}
    __default_agents = [webdriver.Firefox, webdriver.Chrome, webdriver.Ie, webdriver.Edge]

    def __init__(self, *agents):
        self.registry = Registry()

        if len(agents) > 0:
            assert all([isinstance(webdriver, agent) for agent in agents])

        agentlib = {}
        for agent in agents if len(agents) > 0 else self.__default_agents:
            agent_name = str(agent).replace("<class 'selenium.webdriver.", "") \
                                   .replace(".webdriver.WebDriver'>", "")
            agentlib = dict(**agentlib, **{agent_name: agent})

            self.__agents = agentlib

    def browserAction(self, iaction_callbacks: dict):
        for name, agent in self.__agents.items():
            binary_location = self.registry.getInstallLocation(name)
            if binary_location is None or not os.path.exists(binary_location):
                print(f"[ERROR_LOADING_AGENT]: Unable to load program location of {agent}")
                continue

            browser = BrowserBot(browser_exec=binary_location)
            browser.start()

            for iaction_callback, args in iaction_callbacks.items():
                callback = getattr(browser.action, iaction_callback.__name__)
                if isinstance(args, list):
                    print("here", args)
                    callback(*args)
                elif isinstance(args, property):
                    for key, val in BrowserBot.__dict__.items():
                        if str(val) == str(args):
                            callback(getattr(browser, key))
                            break
                else:
                    callback(args)

            browser.release()

executables: list = [
    ("https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC", None)
]

if __name__ == '__main__':
    Configuration()
    both = BotHandler()
    both.browserAction({
        IActions.downloadAddons: BrowserBot.addon_uris,
        IActions.installAddons: BrowserBot.downloads
    })
