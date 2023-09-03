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

MAIN_LINK = "https://www.bezrealitky.cz/vyhledat?offerType=PRODEJ&estateType=BYT&disposition=DISP_1_1&disposition=DISP_2_KK&disposition=DISP_2_1&disposition=DISP_3_KK&disposition=DISP_3_1&regionOsmIds=R435541&page="
LISTING_CLASS = "PropertyCard_propertyCardImageHolder__Dxypp mb-3 mb-md-0 me-md-5 propertyCardImageHolder"
PRICE_ELEM_CLASS = "h4 fw-bold"
TIMEOUT = 20 # seconds

results = []

driver = webdriver.Firefox()
driver.get(MAIN_LINK+str(1))
# Agree to cookies
driver.implicitly_wait(TIMEOUT)
allow_cookie_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
allow_cookie_button.click()

listings_pages = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_all_elements_located((By.XPATH, f'//a[@class="page-link"]')))
last_page = int(listings_pages[-2].text)

for i in range(1, last_page + 1):
    if i != 1:
        driver.get(MAIN_LINK + str(i))
    
    # Get all property listings on a page
    try:
        elements = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.XPATH, f'//div[@class="{LISTING_CLASS}"]//a'))
        )
        print(len(elements))
        prices = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.XPATH, f'//section[contains(@class, "box Section_section__gjwvr section mb-6 mb-md-10")]//span[contains(@class, "PropertyPrice_propertyPriceAmount")]'))
        )
        for elem in prices:
            print(elem.text)
    except TimeoutException:
        # Case when there is an empty page as the last page
        elements = []
    driver.implicitly_wait(TIMEOUT)
    for j, element in enumerate(elements):
        temp_dict = {'Cena': prices[j].text}
        # Slow down of opening of the pages
        time.sleep(3)
        #get href
        href = element.get_attribute('href')
        print(href)
        #open new window with specific href
        driver.execute_script("window.open('" + href +"');")
        # switch to new window
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        tables = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_any_elements_located((By.XPATH, "//tbody"))
        )
        print(len(tables))
        
        for table in tables:
            # names = table.find_elements(By.XPATH, ".//th")
            # values = table.find_elements(By.XPATH, ".//td")
            names = WebDriverWait(table, TIMEOUT).until(
                EC.visibility_of_any_elements_located((By.XPATH, ".//th"))
            )
            values = WebDriverWait(table, TIMEOUT).until(
                EC.visibility_of_any_elements_located((By.XPATH, ".//td"))
            )
            for name, value in zip(names, values):
                temp_dict.update({name.text: value.text})
        results.append(temp_dict)
        
        #close the new window
        driver.implicitly_wait(10)
        driver.close()
        #back to main window
        driver.switch_to.window(driver.window_handles[0])

driver.quit()

with open(f"/Users/Marek/housing_market/raw_data/bezrealitky_raw_{datetime.today().strftime('%Y-%m-%d')}.pkl", mode='wb') as raw_file:
    pickle.dump(results, raw_file)

no_dups_results = [dict(t) for t in {tuple(sorted(d.items())) for d in results}]
errors = 0
records_no_disposition = 0
dispositions = set()
for dict in no_dups_results:
    # Convert the price to Decimal
    try:
        dict['Cena'] = decimal.Decimal(re.sub(r'[^\d]', '', dict['Cena']))
    except decimal.InvalidOperation:
        dict['Cena'] = None
        errors += 1
    try:
        dispositions.add(dict['DISPOZICE'])
    except KeyError:
        dict['DISPOZICE'] = None
        records_no_disposition += 1

print('========Data quality report Bezrealitky=========')
print('Number of scraped offerings:', len(results))
print('Number of duplicates:', len(results) - len(no_dups_results))
print('Number of observations with nonnumeric price:', errors)
print('The dispositions encountered:', dispositions)
print('Records without disposition:', records_no_disposition)

with open(f"/Users/Marek/housing_market/preprocessed_data/bezrealitky_preprocessed_{datetime.today().strftime('%Y-%m-%d')}.pkl", mode='wb') as preprocessed_file:
    pickle.dump(no_dups_results, preprocessed_file)

