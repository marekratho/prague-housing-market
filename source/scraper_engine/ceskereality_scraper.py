from ._scraper import Scraper

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
from datetime import datetime
import time
import re
import decimal

class CeskerealityScraper(Scraper):
    def __init__(self, config) -> None:
        self.driver = webdriver.Firefox()
        self.config = config
        self.current_page = 1
        self.listings = []
    
    def handle_cookie_consent(self) -> None:
        iframes = self.driver.find_elements(By.XPATH, self.config['COOKIE_IFRAME_XPATH'])
        # If there is a cookies iframe that needs to be confirmed
        if len(iframes) != 0:
            print('Number of iframes: ', len(iframes))
            self.driver.switch_to.frame(iframes[0])
            # Click button to accept cookies
            self.driver.find_element(
                By.XPATH, 
                self.config['ACCEPT_COOKIES_BUTTON_XPATH']\
                    .format(ACCEPT_COOKIES_BUTTON_CLASS=self.config['ACCEPT_COOKIES_BUTTON_CLASS'])
            ).click()
            time.sleep(self.config['SLEEP'])
            self.driver.switch_to.parent_frame()
        
        return None
    
    def load_page(self, page_number: int) -> None:
        if page_number == 1:
            self.driver.get(self.config['MAIN_LINK'])
        else:
            self.driver.get(self.config['MAIN_LINK'] + '&strana=' + str(page_number))

    def scrape(self) -> None:
        self.load_page(self.current_page)
        self.handle_cookie_consent()
        elements = [None, ]
        while (len(elements) != 0):
            if self.current_page != 1:
                self.load_page(self.current_page)
            
            # Get all property listings on a page
            try:
                elements = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                    EC.visibility_of_all_elements_located((
                        By.XPATH, 
                        self.config['LISTING_XPATH'].format(LISTING_CLASS=self.config['LISTING_CLASS'])
                    ))
                )
            except TimeoutException:
                # Case when there is an empty page as the last page
                elements = []
            self.driver.implicitly_wait(self.config['TIMEOUT'])
            for element in elements:
                href = element.get_attribute('href')
                # Open new window with specific href
                self.driver.execute_script("window.open('" + href +"');")
                # Switch to new window
                self.driver.switch_to.window(self.driver.window_handles[1])
                try:
                    price = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            self.config['PRICE_XPATH'].format(PRICE_CLASS=self.config['PRICE_CLASS'])
                        ))
                    )
                    temp_dict = {'Cena': price.text}
                    # Get title element which contains disposition and location as subelements
                    title_element = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                        EC.visibility_of_element_located((
                            By.XPATH, 
                            self.config['TITLE_XPATH'].format(TITLE_CLASS=self.config['TITLE_CLASS'])
                        ))
                    )
                    disposition_string = title_element.find_element(By.XPATH, ".//h1").text
                    location_string = title_element.find_element(By.XPATH, ".//h2").text
                    temp_dict.update({'Disposition': disposition_string})
                    temp_dict.update({'Location': location_string})
                    table = WebDriverWait(self.driver, self.config['TIMEOUT']).until(
                        EC.visibility_of_element_located((By.XPATH, "//tbody"))
                    )
                    names = table.find_elements(By.XPATH, ".//th")
                    values = table.find_elements(By.XPATH, ".//td")
                    for name, value in zip(names, values):
                        temp_dict.update({name.text: value.text})
                    
                    self.listings.append(temp_dict)
                except TimeoutException:
                    # The driver was not sucessfull in getting the listing deatils
                    # In case that the page did not load properly
                    # Skip the current listing
                    pass
                # Close the opened tab with listing details
                self.driver.implicitly_wait(10)
                self.driver.close()
                # Back to main window
                self.driver.switch_to.window(self.driver.window_handles[0])
            self.current_page += 1
        
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

            # Parse the title the disposition,
            # area of the apartment and Prague district
            # TODO: Area substring was None
            area_substring = re.search(r'\d+\sm²', dictionary['Disposition'])
            if area_substring:
                dictionary['Area'] = int(re.sub(r'\sm²', '', area_substring.group(),))
                dictionary['District'] = dictionary['Disposition'][area_substring.end() + 1:]
            disposition = re.search(r'\d\+[\w\d]+', dictionary['Disposition'])
            if disposition:
                dictionary['Disposition'] = disposition.group()
            else:
                dictionary['Disposition'] = 'NA'
        
        return no_dups_results

    