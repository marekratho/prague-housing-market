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

MAIN_LINK = "https://www.sreality.cz/hledani/prodej/byty/praha-1,praha-2,praha-3,praha-4,praha-5,praha-6,praha-7,praha-8,praha-9,praha-10?velikost=1%2B1,2%2Bkk,2%2B1,3%2Bkk,3%2B1&stavba=panelova,cihlova&strana="
COOKIE_CONSENT_BUTTON_CLASS = "scmp-btn scmp-btn--default sm-max:scmp-ml-sm md:scmp-ml-md lg:scmp-ml-dialog"
TIMEOUT = 30
counter = 1
driver = webdriver.Firefox()
driver.get(MAIN_LINK + str(counter))
# Agree to cookies
driver.implicitly_wait(TIMEOUT)


allow_cookie_button = WebDriverWait(driver, TIMEOUT).until(
    EC.url_matches("https://www.seznam.cz/nastaveni-souhlasu/")
)

time.sleep(5)
print(driver.page_source)
#driver.switch_to.frame(driver.find_elements(By.TAG_NAME, "iframe")[0])

time.sleep(10)
# WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div"))).click()


ActionChains(driver)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .send_keys(Keys.TAB)\
    .perform()
time.sleep(5)
ActionChains(driver)\
    .send_keys(Keys.ENTER)\
    .send_keys(Keys.RETURN)\
    .perform()


results = []
# How many listings are on sreality?
displayed_results = driver.find_elements(By.XPATH, '//span[@class="numero ng-binding"]')
all_listings_count = int(displayed_results[1].text.replace(' ',''))
print(all_listings_count)
end_reached = False
processed_listings = 0
while not end_reached:
    time.sleep(15)
    current_page_listings = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_all_elements_located((By.XPATH, f'//div[@class="property ng-scope"]')))
    print(len(current_page_listings))
    for listing in current_page_listings:
        price_subelement = listing.find_element(By.XPATH, './/span[@class="price ng-scope"]')
        price = price_subelement.text

        name_subelement = listing.find_element(By.XPATH, './/span[@class="name ng-binding"]')
        name = name_subelement.text
        
        location_subelement = listing.find_element(By.XPATH, './/span[@class="locality ng-binding"]')
        location = location_subelement.text
        results.append({
            'Heading': name,
            'Location': location, 'Cena': price
        })
    # Check if end of page has been reached
    processed_listings += 20
    if processed_listings > all_listings_count:
        end_reached = True
    else:
        counter += 1
        driver.get(MAIN_LINK + str(counter))

time.sleep(10)
driver.quit()

with open(f"/Users/Marek/housing_market/raw_data/sreality_raw_{datetime.today().strftime('%Y-%m-%d')}.pkl", mode='wb') as raw_file:
    pickle.dump(results, raw_file)

no_dups_results = [dict(t) for t in {tuple(sorted(d.items())) for d in results}]
errors = 0
dispositions = set()
for dict in no_dups_results:
    # Convert the price to Decimal
    try:
        dict['Cena'] = decimal.Decimal(re.sub(r'[^\d]', '', dict['Cena']))
    except decimal.InvalidOperation:
        dict['Cena'] = None
        errors += 1
    
    # Split the Heading text into area and disposition
    heading = dict['Heading'].replace('Prodej bytu ', '').split()
    dict['Disposition'] = heading.pop(0)
    dict['Area'] = ''.join(heading)

    dispositions.add(dict['Disposition'])
    
print('========Data quality report Sreality=========')
print('Number of scraped offerings:', len(results))
print('Number of duplicates:', len(results) - len(no_dups_results))
print('Number of observations with nonnumeric price:', errors)
print('The dispositions encountered:', dispositions)

with open(f"/Users/Marek/housing_market/preprocessed_data/sreality_preprocessed_{datetime.today().strftime('%Y-%m-%d')}.pkl", mode='wb') as preprocessed_file:
    pickle.dump(no_dups_results, preprocessed_file)


