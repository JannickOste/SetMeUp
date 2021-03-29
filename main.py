from sys import platform
from time import sleep

from Classes.Registry import Registry
from Classes.Configuration import Configuration
from Browser.BrowserBot import BrowserBot


extensionLib: dict = {
    "chrome":
    [
         "https://chrome.google.com/webstore/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd?hl=en",
         "https://chrome.google.com/webstore/detail/adblock-plus-free-ad-bloc/cfhdojbkjhnklbpkdaibdccddilifddb?hl=en",
         "https://chrome.google.com/webstore/detail/pop-up-blocker-for-chrome/bkkbcggnhapdmkeljlodobbkopceiche?hl=en",
         "https://chrome.google.com/webstore/detail/darkify/lchabmjccahchaflojonfbepjbbnipfc"
    ],
    "firefox":
    [
        "https://addons.mozilla.org/en-US/firefox/addon/lastpass-password-manager/",
        "https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/",
        "https://addons.mozilla.org/en-US/firefox/addon/popup-blocker-ultimate/"
    ]
}

executables: list = [
    ("https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC", None)
]


def downloadExtensions():
    registry = Registry()
    exec_downloaded = platform != "win32"

    for agent in extensionLib.keys():
        binary_location = registry.getInstallLocation(agent)
        if binary_location is None:
            print(f"[ERROR_LOADING_AGENT]: Failed to load agent {agent}")
            continue

        browser = BrowserBot(browser_exec=binary_location)
        browser.start()
        if not exec_downloaded:
            browser.action.downloadExecutables(executables)
            exec_downloaded = True

        browser.release()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Configuration()
    downloadExtensions()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
