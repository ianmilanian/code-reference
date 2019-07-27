import time

from tqdm import tqdm_notebook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def focus_window():
    time.sleep(.5)
    ActionChains(browser).send_keys(Keys.ESCAPE).perform()

def find_elements(xpath):
    time.sleep(.1)
    return browser.find_elements_by_xpath(xpath)

def delete_element():
    try:
        browser.execute_script("arguments[0].parentNode.removeChild(arguments[0])", element)
    except:
        return False
    return True

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("disable-gpu")
options.add_argument("disable-audio")
options.add_argument("start-maximized")
options.add_argument("log-level=3")
options.add_argument("disable-bundled-ppapi-flash")
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

url     = "https://twitter.com/realDonaldTrump?lang=en"
content = "//li[contains(@class, 'js-stream-item stream-item')]"
browser = webdriver.Chrome(chrome_options = options)
browser.get(url)

with open("data.txt", "w", encoding="utf-8") as f, tqdm_notebook() as pbar:
    focus_window()
    while find_elements(content):
        for element in find_elements(content):
            text = element.find_element_by_xpath("//div[@class='js-tweet-text-container']").text
            date = element.find_element_by_xpath("//span[contains(@class, '_timestamp')]").get_attribute("data-time")
            delete_element()
            f.write("{},{}\n".format(date, text))
            pbar.update()
        for _ in range(5):
            if not len(find_elements(content)):
                ActionChains(browser).send_keys(Keys.HOME).perform()
                time.sleep(.1)
                ActionChains(browser).send_keys(Keys.END).perform()
            else:
                break
browser.quit()
