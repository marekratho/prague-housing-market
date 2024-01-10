from ._scraper import Scraper
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Union
import pickle
from datetime import datetime
import time
import re
import decimal


class BezrealitkyScraper(Scraper):
    def __init__(self, config) -> None:
        self.driver = webdriver.Firefox()
        self.config = config
        self.current_page = 1
        self.listings = []
    
    def load_page(self, page_number: int) -> None:
        self.driver.get(self.config['MAIN_LINK'] + str(page_number))
    
    def handle_cookie_consent(self) -> None:
        allow_cookies_button = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
            EC.visibility_of_element_located((By.ID, self.config['COOKIES_BUTTON']))
        )
        allow_cookies_button.click()
    
    def get_total_page_count(self) -> int:
        listings_pages = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
            EC.visibility_of_all_elements_located((By.XPATH, self.config['LISTING_PAGES_XPATH']))
        )
        return int(listings_pages[-2].text)

    def get_listing_details(self, href) -> dict:
        # Open new window with the listing URL and swith to it
        self.driver.execute_script("window.open('" + href +"');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        
        # Introduce sleep to slow down the scraping to avoid timneouts
        time.sleep(2)

        # Locate table elements that contain listing details
        try:
            tables = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                EC.visibility_of_any_elements_located((By.XPATH, "//tbody"))
            )
        except TimeoutException:
            tables = []

        # Scrape details from the tables
        listing_details = {}
        for table in tables:
            names = WebDriverWait(table, self.config['TIMEOUT']).until(
                EC.visibility_of_any_elements_located((By.XPATH, ".//th"))
            )
            values = WebDriverWait(table, self.config['TIMEOUT']).until(
                EC.visibility_of_any_elements_located((By.XPATH, ".//td"))
            )
            for name, value in zip(names, values):
                if name.text != '':
                    listing_details.update({name.text: value.text})
        
        # Close the window and switch driver to the main window
        self.driver.implicitly_wait(10)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        return listing_details
    
    def scrape_attempt(self, total_listings: int) -> Union[list, None]:
    
        for i in range(self.current_page, total_listings + 1):
            result_list = []
            try:
                # Get individual listing links and their prices on the current page
                listings = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                    EC.visibility_of_all_elements_located((By.XPATH, self.config['LISTING_XPATH'].format(LISTING_CLASS=self.config['LISTING_CLASS'])))
                )
                
                prices = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                    EC.presence_of_all_elements_located((By.XPATH, self.config['PRICE_XPATH'].format(
                        PRICE_SECTION_CLASS=self.config['PRICE_SECTION_CLASS'],
                        PRICE_SPAN_CLASS=self.config['PRICE_SPAN_CLASS']
                    )))
                )
            except TimeoutException:
                listings = []
                prices = []
            
            for listing, price in zip(listings, prices):
                time.sleep(self.config['SLEEP'])
                listing_data = self.get_listing_details(listing.get_attribute('href'))
                # Add price to the listing data and append to the scraper results
                result_list.append(listing_data.__setitem__('Cena', price.text) or listing_data)
            
            self.current_page += 1
            self.load_page(self.current_page)

            # Add the scraped listings from the current page only after
            # the entire page has been scraped to avoid duplicates in
            # case of TimeoutError
            self.listings += result_list

        return None
    
    def scrape(self, total_attemps:int = 10) -> None:
        self.load_page(self.current_page)
        self.handle_cookie_consent()
        total_listing_pages = self.get_total_page_count()

        for i in range(total_attemps):
            try:
                self.scrape_attempt(total_listings=total_listing_pages)
                break
            except UnexpectedAlertPresentException:
                '''
                While scraping listings from bezrealitky, a pop-up can occur
                which causes the scraping to timeout and fail. A solution
                is to repeat the scraping starting from the listing page
                where the last timeout occurred.
                '''
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

                self.load_page(self.current_page)
        
        self.driver.quit()
        
        return None
    
    def process_listing_data(self) -> list:
        raw_listings = self.listings.copy()
        # Purge duplicate records
        no_dups_results = [dict(t) for t in {tuple(sorted(d.items())) for d in raw_listings}]
        for dictionary in no_dups_results:
            # Convert the price to Decimal
            try:
                dictionary['Cena'] = decimal.Decimal(re.sub(r'[^\d]', '', dictionary['Cena']))
            except decimal.InvalidOperation:
                dictionary['Cena'] = None
            if 'DISPOZICE' not in dictionary.keys():
                dictionary['DISPOZICE'] = None
        
        return no_dups_results
            
