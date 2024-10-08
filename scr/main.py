from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

from scraping import scrape_pricing_details

url = 'https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/'

regions =[('us-east', 'usd'),
         ('spain-central', 'eur')]

def open_webpage(url='https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/',
                 maximize=False,
                 width=1000,
                 height=1080):

    # Setup Chrome options
    chrome_options = Options()

    # Uncomment the next line to run Chrome in headless mode (no GUI)
    # chrome_options.add_argument('--headless')

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service,
                              options=chrome_options)

    try:
        # Maximize the browser window or set to specific size
        if maximize:
            driver.maximize_window()
        else:
            driver.set_window_size(width, height)

        # Navigate to the URL
        driver.get(url)

        princing_regions = {}

        for region in regions:
            region_value, currency_value = region
            key_region = region_value + currency_value
            option_select(driver=driver, dropdown_id='region-selector', value=region_value)
            option_select(driver=driver, dropdown_id='currency-selector', value=currency_value)

            # Optional: Wait until the page updates based on the selected region
            # This can be customized based on specific page behavior after selection
            time.sleep(1)  # Adjust as needed

            pricing_details = scrape_pricing_details(driver,region_value,currency_value)

            princing_regions[key_region] = pricing_details

            print('\n','='*50)
            import pprint
            pprint.pprint(pricing_details)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

def option_select(driver, dropdown_id, value):
    print(f"Attempting to select '{value}' in dropdown with id='{dropdown_id}'....", end=' ')
    try:
        # Initialize WebDriverWait
        wait = WebDriverWait(driver, 20)  # 20 seconds timeout

        # Wait until the select element is present and clickable
        select_element = wait.until(
            EC.element_to_be_clickable((By.ID, dropdown_id))
        )

        # Initialize Select class
        select = Select(select_element)

        # Select the desired value by value
        select.select_by_value(value)
        print(f"Successfully selected '{value}' in '{dropdown_id}'.\n")

    except TimeoutException:
        print(f"Timeout: Dropdown with id '{dropdown_id}' was not clickable within the given time.")
    except NoSuchElementException:
        print(f"No such element: Dropdown with id '{dropdown_id}' was not found on the page.")
    except Exception as e:
        print(f"An unexpected error occurred while selecting '{value}' in '{dropdown_id}': {e}")




if __name__ == "__main__":
    open_webpage()