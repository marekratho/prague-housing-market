from ._scraper import Scraper
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pickle
import re
import decimal
from datetime import datetime
from typing import Union

class SrealityScraper(Scraper):
    def __init__(self, config) -> None:
        self.driver = webdriver.Firefox()
        self.config = config
        self.current_page = 1
        self.listings = []
    
    def load_page(self, page_number: int) -> None:
        self.driver.get(self.config['MAIN_LINK'] + str(page_number))
    
    def handle_cookie_consent(self) -> None:
        WebDriverWait(self.driver, self.config['TIMEOUT']).until(
            EC.url_matches(self.config['COOKIE_CONSENT_URL'])
        )
        time.sleep(self.config['SLEEP'])

        # Elements in the Cookie consent Iframe are hidden in a Shadowroot
        # Use TAB keys to navigate to the button
        move_to_allow_button = ActionChains(self.driver)
        for i in range(7):
            move_to_allow_button.send_keys(Keys.TAB)
        move_to_allow_button.perform()

        time.sleep(5)
        # Hit enter button to agree to cookies
        ActionChains(self.driver)\
            .send_keys(Keys.ENTER)\
            .send_keys(Keys.RETURN)\
            .perform()
        time.sleep(self.config['SLEEP'])
        self.load_page(self.current_page)
        time.sleep(self.config['SLEEP'])
        return None
    
    def get_total_listing_count(self) -> int:
        displayed_results = self.driver.find_elements(
            By.XPATH, 
            self.config['TOTAL_LISTING_COUNT_XPATH']\
                .format(LISTING_COUNT_CLASS=self.config["LISTING_COUNT_CLASS"])
        )
        return int(displayed_results[1].text.replace(' ',''))
    
    def scrape(self) -> Union[list, None]:
        self.load_page(self.current_page)
        self.handle_cookie_consent()

        end_reached = False
        processed_listings = 0
        total_listings = self.get_total_listing_count()

        while not end_reached:
            time.sleep(self.config['SLEEP'])
            current_page_listings = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                EC.visibility_of_all_elements_located((
                    By.XPATH, 
                    self.config['LISTING_XPATH'].format(LISTING_CLASS=self.config['LISTING_CLASS'])
                ))
            )

            for listing in current_page_listings:
                price_subelement = listing.find_element(
                    By.XPATH, 
                    self.config['PRICE_XPATH'].format(PRICE_CLASS=self.config['PRICE_CLASS'])
                )
                price = price_subelement.text

                name_subelement = listing.find_element(
                    By.XPATH, 
                    self.config['NAME_XPATH'].format(NAME_CLASS=self.config['NAME_CLASS'])
                )
                name = name_subelement.text
                
                location_subelement = listing.find_element(
                    By.XPATH, 
                    self.config['LOCATION_XPATH'].format(LOCATION_CLASS=self.config['LOCATION_CLASS'])
                )
                location = location_subelement.text

                self.listings.append({
                    'Heading': name,
                    'Location': location, 
                    'Cena': price
                })
            
            # Check if end of page has been reached
            processed_listings += 20
            if processed_listings > total_listings:
                end_reached = True
            else:
                self.current_page += 1
                self.load_page(self.current_page)
        
        self.driver.quit()
            
        return None
    
    def process_listing_data(self) -> list:
        raw_listings = self.listings.copy()
        # Purge duplicate records
        no_dups_results = [dict(t) for t in {tuple(sorted(d.items())) for d in raw_listings}]

        for listing in no_dups_results:
            # Convert string price to numeric
            try:
                listing['Cena'] = decimal.Decimal(re.sub(r'[^\d]', '', listing['Cena']))
            except decimal.InvalidOperation:
                listing['Cena'] = None

            # Parse heading of the listing into parts
            heading = listing['Heading'].replace('Prodej bytu ', '').split()
            listing['Disposition'] = heading.pop(0)
            listing['Area'] = ''.join(heading)
        
        return no_dups_results
