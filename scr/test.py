from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

url = 'https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/'
region_value = 'spain-central'
currency_value = 'eur'

def open_webpage(url, maximize=True, width=1920, height=1080):
    # Setup Chrome options
    chrome_options = Options()

    # Uncomment the next line to run Chrome in headless mode (no GUI)
    # chrome_options.add_argument('--headless')

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Maximize the browser window or set to specific size
        if maximize:
            driver.maximize_window()
        else:
            driver.set_window_size(width, height)

        # Navigate to the URL
        driver.get(url)

        # Select Region
        option_select(driver=driver, dropdown_id='region-selector', value=region_value)

        # Select Currency
        option_select(driver=driver, dropdown_id='currency-selector', value=currency_value)

        # Optional: Wait until the page updates based on the selected region
        # This can be customized based on specific page behavior after selection
        time.sleep(5)  # Adjust as needed

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

def option_select(driver, dropdown_id, value):
    print(f"Attempting to select '{value}' in dropdown with id='{dropdown_id}'")
    try:
        # Initialize WebDriverWait
        wait = WebDriverWait(driver, 20)  # 20 seconds timeout

        # Wait until the select element is present and clickable
        select_element = wait.until(
            EC.element_to_be_clickable((By.ID, dropdown_id))
        )

        # Initialize Select class
        select = Select(select_element)

        # Retrieve all options
        all_options = select.options

        # Prepare lists to hold values and texts
        options_data = []

        print(f"\nAvailable options in '{dropdown_id}':\n")
        for option in all_options:
            option_value = option.get_attribute('value')
            option_text = option.text
            aria_disabled = option.get_attribute('aria-disabled')
            is_disabled = aria_disabled == 'true'
            status = "Disabled" if is_disabled else "Enabled"
            print(f"Value: '{option_value}' | Text: '{option_text}' | Status: {status}")
            options_data.append((option_value, option_text, is_disabled))

        # Update the condition to include options not explicitly disabled
        enabled_options = [opt[0] for opt in options_data if opt[2] == False]

        if value not in enabled_options:
            print(f"\nThe value '{value}' is either disabled or does not exist in '{dropdown_id}'.")
            return

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
    target_url = 'https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/'
    open_webpage(target_url)