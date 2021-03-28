import os
from os import listdir

from Classes.Configuration import Configuration
from Classes.Registry import Registry
from Drivers.BrowserBot import BrowserBot

registry = Registry()

extensionLib: dict = {
    "firefox":
    [
        "https://addons.mozilla.org/en-US/firefox/addon/lastpass-password-manager/",
        "https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/",
        "https://addons.mozilla.org/en-US/firefox/addon/popup-blocker-ultimate/"
    ]
    # "chrome":
    # [
    #      #"https://chrome.google.com/webstore/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd?hl=en"
    #      #"https://chrome.google.com/webstore/detail/adblock-plus-free-ad-bloc/cfhdojbkjhnklbpkdaibdccddilifddb?hl=en",
    #      #"https://chrome.google.com/webstore/detail/pop-up-blocker-for-chrome/bkkbcggnhapdmkeljlodobbkopceiche?hl=en",
    #      #"https://chrome.google.com/webstore/detail/darkify/lchabmjccahchaflojonfbepjbbnipfc"
    # ]
}


def downloadExtensions():
    for agent in extensionLib.keys():
        binary_location = registry.getInstallLocation(agent)
        browser = BrowserBot(binary_location)
        browser.start()
        browser.downloadAddons(extensionLib.get(agent))
        browser.installAddons()

        browser.release()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Configuration()
    downloadExtensions()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
