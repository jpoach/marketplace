from splinter import Browser, Config
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup as soup
import pandas as pd
import time
# import requests
from datetime import datetime
from tabulate import tabulate
import git
import os
import argparse
import hashlib
from get_proxies import get_proxies
from plot import plot_generic

parser = argparse.ArgumentParser(description="Filter listings based on criteria.")

parser.add_argument("--base-url", type=str, default="https://www.facebook.com/marketplace/108205955874066/search?", help="Base url (determines location)")

parser.add_argument("--name", type=str, default="FordEscape", help="Name of the item")
parser.add_argument("--min-price", type=int, default=100, help="Minimum price of the item")
parser.add_argument("--max-price", type=int, default=2500, help="Maximum price of the item")
parser.add_argument("--days-listed", type=int, default=1, help="Maximum number of days the item has been listed")
parser.add_argument("--radius", type=int, default=500, help="Search radius")

parser.add_argument("--scroll-count", type=int, default=10, help="Scroll count")
parser.add_argument("--scroll-delay", type=int, default=2, help="Scroll delay")

parser.add_argument("--headless", action="store_true", help="Browser config option")
parser.add_argument("--proxy", action="store_true", help="Use proxies")

args = parser.parse_args()


# Set up base url
base_url = args.base_url

# Set up search parameters
name = args.name
min_price = args.min_price
max_price = args.max_price
days_listed = args.days_listed

#Set up full url
url = f"{base_url}minPrice={min_price}&maxPrice={max_price}&daysSinceListed={days_listed}&query={name}&exact=false"

# Define the number of times to scroll the page
scroll_count = args.scroll_count

# Define the delay (in seconds) between each scroll
scroll_delay = args.scroll_delay

# Set up Splinter
mobile_user_agent = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en)'
config = Config(user_agent=mobile_user_agent, incognito=True, headless=args.headless)

chrome_options = Options()
chrome_options.add_argument('--disable-cache')

proxies = get_proxies()
proxy = proxies.pop(0)

#repo_path = "/home/daniel/git/marketplace"
#repo_url = "https://github.com/daniel-campa/marketplace.git"

repo_path = "/Users/thepo/Desktop/marketplace"
repo_url = "https://github.com/jpoach/marketplace.git"


content_path = os.path.join(repo_path, 'docs', 'index.html')
csv_path = os.path.join(repo_path, 'docs', 'listings.csv')

radius_list = [1,2,5,10,20,40,60,80,100,250,500]


while True:
    try:
        # proxy = 'http://143.107.199.248:8080'
        if args.proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
            print(proxy)

        with Browser('chrome', config=config, options=chrome_options) as browser:
            browser.driver.maximize_window()
            browser.cookies.delete_all()

            # Visit the website
            browser.visit(url)

            if browser.is_element_present_by_css('div[aria-label="Close"]', wait_time=5):
                browser.find_by_css('div[aria-label="Close"]').first.click()

            if not browser.is_element_present_by_css('a[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1lku1pv"]', wait_time=10):
                if args.proxy:
                    # rotate proxy
                    proxy = proxies.pop(0)
                    continue

            if browser.is_element_present_by_css('div[aria-label="OK"]', wait_time=5):
                proxy = proxies.pop(0)
            elif browser.is_element_present_by_css('div[class="x1iyjqo2"]', wait_time=5):
                try:
                    browser.find_by_css('div[class="x1iyjqo2"]').first.click()
                    time.sleep(2)
                    browser.find_by_css('div[class="x78zum5"]').first.click()
                    time.sleep(2)

                    try:
                        radius_id = radius_list.index(args.radius)
                    except ValueError:
                        print('using radius 40')
                        radius_id = 5
                    browser.find_by_css('div[role="option"]')[radius_id].click()
                    time.sleep(0.5)
                    browser.find_by_css('div[aria-label="Apply"]').first.click()

                except:
                    print('warning: unable to change radius')




            # Loop to perform scrolling
            for _ in range(scroll_count):
                # Execute JavaScript to scroll to the bottom of the page
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Pause for a moment to allow the content to load
                time.sleep(scroll_delay)

            # Create a BeautifulSoup object from the scraped HTML
            market_soup = soup(browser.html, 'html.parser')

            browser.cookies.delete_all()



        listings = market_soup.find_all('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1lku1pv')

        if os.path.exists(csv_path):
            listings_df = pd.read_csv(csv_path, index_col=0)
        else:
            listings_df = pd.DataFrame()

        for item in listings:
            item_link = 'https://www.facebook.com' + item.attrs['href']
            # image_link = item.findChild('img').attrs['src']
            item_data_div = item.findChild('div', class_='x9f619 x78zum5 xdt5ytf x1qughib x1rdy4ex xz9dl7a xsag5q8 xh8yej3 xp0eagm x1nrcals')

            text_data = [item_data.text for item_data in item_data_div.children]

            try:
                price = text_data[0].split('$')[1]
            except IndexError:
                price = text_data[0]
            if type(price) == str:
                if price == '':
                    price = pd.NA
                else:
                    price = price.replace(',','')
                    price = price.lower().replace('us','')
                    price = round(float(price))
            try:
                assert type(price) is int
            except AssertionError as e:
                print(e)
                print(type(price), price)
            name = text_data[1]
            location = text_data[2]

            try:
                city, state = location.split(', ')
            except ValueError:
                print(location)
                city, state = location, location

            if len(text_data) > 3:
                extra = text_data[3:]
            else:
                extra = []
    
            row_str = "|".join([name, str(price), location])
            hash = hashlib.sha256(row_str.encode()).hexdigest()
            
            item_dict = {
                'hash': hash,
                'time': datetime.now().strftime("%m/%d %H:%M"),
                'name': name,
                'price': price,
                'city': city,
                'state': state,
                'extra': extra,
                'link': item_link
                # 'image': image_link
            }

            item_df = pd.DataFrame([item_dict]).set_index(['hash'])

            if hash not in listings_df.index:
                listings_df = pd.concat([listings_df, item_df])

        # if listings_df.price.dtype == 'O':
            # listings_df.price = listings_df.price.str.replace(',','').astype(int)

        out_df = listings_df.sort_values(['price'])

        
        # listings_df.image = listings_df.image.apply(lambda img_link: f'<img src={img_link} alt="{img_link}" >')
        # out_df.drop(['image'], axis=1, inplace=True)

        listings_df.to_csv(csv_path)

        print(
            tabulate(out_df, headers='keys', tablefmt='psql', showindex=False, maxcolwidths=[7, 30, 6, 17, 5, 10, 70])
        )

        pd.set_option('display.max_colwidth', None)

        
        print(
            datetime.now().strftime("%m/%d %H:%M"),
            proxy if args.proxy else '|no proxy|',
            out_df.shape
        )

        plot_generic(df=listings_df)

        with open(content_path, 'w') as f:
            f.write('\n<img src="docs/generic_hist.png" alt="price histogram">')
            out_df.to_html(f, index=False, render_links=True, classes=['w3-table-all w3-hoverable'])
            f.write('\n<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">')


        repo = git.Repo(repo_path)
        repo.git.add(all=True)
        repo.index.commit("Updated dashboard")
        origin = repo.remote(name="origin")
        origin.push()

        time.sleep(900)
    
    except WebDriverException as e:
        print(e)
        proxy = proxies.pop(0)
        continue

    except KeyboardInterrupt:
        print()
        break

