import os
import sys
import time
import pickle
import sqlite3
import requests
import traceback
import win32crypt

from selenium import webdriver
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import *
from contextlib import ExitStack
from contextlib import contextmanager

BUNDLED_PATH = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

manifest = \ # static/extension/manifest.json
"""
{
  "manifest_version": 2,
  "name": "JSI Extension",
  "version": "1.0.0",
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["inject.js"],
      "run_at": "document_start"
    }
  ]
}
"""

inject = \ # static/extension/inject.js
"""
const script = document.createElement('script');

script.innerHTML = `
    Object.defineProperty(window.navigator, 'webdriver', {
        get: () => false,
    });
    
    window.chrome = {
        "app":{
            "isInstalled":false
        },
        "webstore": {
            "onInstallStageChanged": {},
            "onDownloadProgress": {}
        },
        "runtime": {
            "PlatformOs": {
                "MAC":"mac",
                "WIN":"win",
                "ANDROID":"android",
                "CROS":"cros",
                "LINUX":"linux",
                "OPENBSD":"openbsd"
            },
            "PlatformArch": {
                "ARM":"arm",
                "X86_32":"x86-32",
                "X86_64":"x86-64",
                "MIPS":"mips",
                "MIPS64":"mips64"
            },
            "PlatformNaclArch": {
                "ARM":"arm",
                "X86_32":"x86-32",
                "X86_64":"x86-64",
                "MIPS":"mips",
                "MIPS64":"mips64"
            },
            "RequestUpdateCheckStatus": {
                "THROTTLED":"throttled",
                "NO_UPDATE":"no_update",
                "UPDATE_AVAILABLE":"update_available"
            },
            "OnInstalledReason": {
                "INSTALL":"install",
                "UPDATE":"update",
                "CHROME_UPDATE":"chrome_update",
                "SHARED_MODULE_UPDATE":"shared_module_update"
            },
            "OnRestartRequiredReason": {
                "APP_UPDATE":"app_update",
                "OS_UPDATE":"os_update",
                "PERIODIC":"periodic"
            }
        }
    };
    
    Object.defineProperty(window.navigator, 'languages', {
        get: () => ['en-US', 'en'],
    });
    
    const getParameter = WebGLRenderingContext.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37445)
            return 'Google Inc.';
        // UNMASKED_RENDERER_WEBGL
        if (parameter === 37446)
            return '(Intel(R) HD Graphics Direct3D11)';
        return getParameter(parameter);
    };
    
    // Remove the injected script after we're done.
    document.currentScript.parentElement.removeChild(document.currentScript);
`;

document.documentElement.prepend(script)
"""

pyinstaller = \ # project.spec
"""
# -*- mode: python -*-

block_cipher = None

a = Analysis(
    ['C:\\user\\project\\script.py'],
    pathex=['C:\\user\\project'],
    binaries=[],
    datas=[
        ('static/extension/*',      'static/extension'),
        ('static/chromedriver.exe', 'static')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='project',
    debug=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
    icon='project.ico')
"""

def save_cookies(self, domain):
    cookie_jar  = requests.cookies.RequestsCookieJar()
    cookie_path = os.path.join(os.getenv('LOCALAPPDATA'), "Google", "Chrome", "User Data", "Default", "Cookies")
    with sqlite3.connect(cookie_path) as db:
        for row in db.execute("SELECT host_key, path, is_secure, expires_utc, name, encrypted_value FROM cookies").fetchall():
            host, path, secure, expires, name, encrypted_value = row
            value  = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8")
            cookie_jar.set(name, value, domain=host, path=path, secure=secure, expires=expires, discard=False)

    if not os.path.isfile("cookies.pkl"):
        cookies, valid = [], False
        for cookie in cookie_jar:
            if domain in cookie.domain:
                cookie_dict = {"domain": cookie.domain, "name": cookie.name, "value": cookie.value, "secure": cookie.secure}
                if "JSESSIONID" in cookie.name:
                    valid = True
                if cookie.expires:
                    cookie_dict["expiry"] = cookie.expires
                if cookie.path_specified:
                    cookie_dict["path"]   = cookie.path
                cookies.append(cookie_dict)
        if not valid:
            raise Exception("Please login to platform from Chrome before continuing.")
        pickle.dump(cookies, open("cookies.pkl", "wb"))
    return cookie_jar

class Browser:
    def __init__(self, headless=True, experimental=False):
        self.browser    = None
        self.min_date   = (datetime.now() - timedelta(days=days)).date()
        self.session    = requests.Session()
        self.options    = webdriver.ChromeOptions()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
        
        if experimental:
            self.options.add_argument(f'load-extension={BUNDLED_PATH}/static/extension/')
        elif headless:
            self.options.add_argument("headless")
        
        self.options.add_argument("disable-gpu")
        self.options.add_argument("disable-audio")
        self.options.add_argument("start-maximized")
        self.options.add_argument("log-level=3")
        self.options.add_argument("disable-infobars")
        self.options.add_argument(f"user-agent={self.user_agent}")
        self.options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images":2})
        self.session.headers = {"Accept-Language": "en-US,en;q=0.5"}
    
    def __enter__(self):
        self.browser = webdriver.Chrome(f"{BUNDLED_PATH}/static/chromedriver.exe", chrome_options=self.options)
        self.browser.get("") # login page
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            self.browser.add_cookie(cookie)
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        if self.browser:
            self.browser.quit()
            self.browser = None
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        return True

if __name__ == "__main__":
    with Browser() as browser:
        browser.get("") # content page
