from splinter import Browser, Config
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
import time

def get_proxies():
    config = Config(incognito=True, headless=True)

    with Browser('chrome', config=config) as browser:
        browser.driver.maximize_window()
        browser.cookies.delete_all()

        browser.visit('https://free-proxy-list.net/')

        time.sleep(2)
        
        proxy_soup = soup(browser.html, 'html.parser')

        browser.cookies.delete_all()


    table = proxy_soup.find('table', class_='table table-striped table-bordered')

    proxies = []
    for tr in table.findChild('tbody').findChildren('tr'):
        children = tr.findChildren('td')
        address, port = children[0].text, children[1].text
        https = True if children[6].text == 'yes' else False

        # proxy = {
        #     'http': f'http://{ip}:{port}'
        # }
        # if https:
        #     proxy['https'] = f'https://{ip}:{port}'
        proxy = f'http://{address}:{port}'

        proxies.append(proxy)
    
    return proxies