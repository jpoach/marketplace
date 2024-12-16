from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as soup
from tabulate import tabulate
import pandas as pd
import time
import git
import os
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Filter car listings based on criteria.")

parser.add_argument("--base-url", type=str, default="https://www.facebook.com/marketplace/108205955874066/search/?", help="Base URL")
parser.add_argument("--min-price", type=int, default=575, help="Minimum price of the car")
parser.add_argument("--max-price", type=int, default=2900, help="Maximum price of the car")
parser.add_argument("--days-listed", type=int, default=1, help="Maximum number of days the car has been listed")
parser.add_argument("--min-mileage", type=int, default=20000, help="Minimum mileage of the car")
parser.add_argument("--max-mileage", type=int, default=140000, help="Maximum mileage of the car")
parser.add_argument("--min-year", type=int, default=2004, help="Earliest year of the car model")
parser.add_argument("--max-year", type=int, default=2012, help="Latest year of the car model")
parser.add_argument("--search", type=str, default="fordescape", help="Search term")
parser.add_argument("--scroll-count", type=int, default=10, help="Scroll count")
parser.add_argument("--scroll-delay", type=int, default=2, help="Scroll delay")

args = parser.parse_args()

# Prepare URL and options
base_url = args.base_url
url = f"{base_url}minPrice={args.min_price}&maxPrice={args.max_price}&daysSinceListed={args.days_listed}&maxMileage={args.max_mileage}&maxYear={args.max_year}&minMileage={args.min_mileage}&minYear={args.min_year}&query={args.search}&exact=false"

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")

# Set up paths and Git
repo_path = "C:\\Users\\thepo\\Desktop\\marketplace"
repo_url = "https://github.com/jpoach/marketplace.git"
content_path = os.path.join(repo_path, "docs\\index.html")

while True:
    try:
        # Initialize WebDriver
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        browser.get(url)

        # Handle pop-ups if present
        try:
            close_button = browser.find_element(By.XPATH, '//div[@aria-label="Close" and @role="button"]')
            close_button.click()
        except:
            pass

        try:
            ok_button = browser.find_element(By.XPATH, '//div[@aria-label="OK" and @role="button"]')
            ok_button.click()
        except:
            pass

        # Scroll to load content
        for _ in range(args.scroll_count):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(args.scroll_delay)

        # Parse the loaded HTML
        market_soup = soup(browser.page_source, 'html.parser')
        browser.quit()

        # Extract listings
        listings = market_soup.find_all(
            'a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1lku1pv')

        listings_df = pd.DataFrame()

        for item in listings:
            try:
                item_link = item.attrs['href']
                image_link = item.findChild('img').attrs['src']
                item_data_div = item.findChild('div', class_='x9f619 x78zum5 xdt5ytf x1qughib x1rdy4ex xz9dl7a xsag5q8 xh8yej3 xp0eagm x1nrcals')

                price, name, location, mileage = [item_data.text for item_data in item_data_div.children]
                city, state = location.split(', ')

                item_dict = {
                    'name': name,
                    'price': price.replace("$", " "),
                    'mileage': mileage,
                    'city': city,
                    'state': state,
                    'link': item_link,
                    'image': image_link
                }

                listings_df = pd.concat([listings_df, pd.DataFrame([item_dict])], ignore_index=False)
            except Exception as e:
                print(f"Error processing item: {e}")

        # Format data
        listings_df.link = 'https://www.facebook.com' + listings_df.link
        listings_df.link = listings_df.link.apply(lambda link: f'<a href="{link}" target="_blank">{link}</a>')
        listings_df.image = listings_df.image.apply(lambda img_link: f'<img src={img_link} alt="{img_link}" >')

        pd.set_option('display.max_colwidth', None)

        out_df = listings_df.sort_values(['price'])
        out_df.drop(['image'], axis=1, inplace=True)

        print(tabulate(out_df, headers='keys', tablefmt='psql', showindex=False, maxcolwidths=[60, 6, 10, 17, 5, 70]))
        out_df.to_html(content_path, index=False, escape=False, classes=['table table-stripped'])
        print(out_df.shape)

        # Push to Git
        repo = git.Repo(repo_path)
        repo.git.add(all=True)
        repo.index.commit("Updated dashboard")
        origin = repo.remote(name="origin")
        origin.push()

        time.sleep(900)  # Wait 15 minutes before refreshing

    except KeyboardInterrupt:
        print("Script interrupted by user.")
        break

    except Exception as e:
        print(f"An error occurred: {e}")
        break
