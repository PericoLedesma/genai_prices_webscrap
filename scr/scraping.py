
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

def scrape_pricing_details(driver, region_value, currency_value):
    print(f"\nScraping pricing details of {region_value}/{currency_value} ...")
    print('---------------------------')

    """
    Scrapes all pricing details from the 'pricing' section of the webpage.

    Args:
        driver (webdriver): Selenium WebDriver instance.

    Returns:
        dict: Nested dictionary containing pricing details categorized accordingly.
    """
    pricing_data = {}

    try:
        # Wait until the pricing section is present
        wait = WebDriverWait(driver, 20)
        pricing_section = wait.until(
            EC.presence_of_element_located((By.ID, "pricing"))
        )
        print("Pricing section found. Starting to scrape pricing details.")

        # Get the inner HTML of the pricing section
        pricing_html = pricing_section.get_attribute('innerHTML')

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(pricing_html, 'html.parser')

        # Iterate through each category (h3 tags denote categories)
        categories = soup.find_all('h3')
        for category in categories:
            category_name = category.get_text(strip=True)
            print(f"Processing category: {category_name}")
            pricing_data[category_name] = {}

            # Locate the next sibling div with class 'row row-size3 column'
            sibling_div = category.find_next_sibling('div', class_='row row-size3 column')
            if not sibling_div:
                # Attempt alternative matching if exact class match fails
                sibling_div = category.find_next_sibling('div', class_=lambda
                    x: x and 'row' in x and 'row-size3' in x and 'column' in x)
                if not sibling_div:
                    print(f"Could not find sibling div for category '{category_name}'. Skipping.")
                    continue

            tables = sibling_div.find_all('table')
            if not tables:
                # Some categories might have no tables (e.g., Assistants API has a table and some paragraphs)
                print(f"No tables found under category '{category_name}'. Skipping.")
                continue

            for table in tables:
                # Extract headers
                headers = []
                thead = table.find('thead')
                if thead:
                    header_cells = thead.find_all('th')
                    headers = [th.get_text(strip=True) for th in header_cells]
                else:
                    print(f"No header found in table under category '{category_name}'. Skipping table.")
                    continue

                # Identify the index of the 'Models' column
                try:
                    models_index = headers.index('Models')
                except ValueError:
                    print(f"'Models' column not found in table under category '{category_name}'. Skipping table.")
                    continue

                # Extract rows
                tbody = table.find('tbody')
                if not tbody:
                    print(f"No tbody found in table under category '{category_name}'. Skipping table.")
                    continue

                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if not cells or len(cells) <= models_index:
                        continue  # Skip empty rows or rows without enough cells

                    # Extract the model name using the 'Models' column
                    model_cell = cells[models_index]
                    model_text = model_cell.get_text(strip=True)

                    if not model_text:
                        continue  # Skip if model name is empty

                    # Initialize the model's data dictionary
                    model_data = {}

                    for idx, cell in enumerate(cells):
                        if idx == models_index:
                            continue  # Skip the 'Models' column as it's used as the key

                        header = headers[idx] if idx < len(headers) else f"Column_{idx + 1}"
                        cell_text = cell.get_text(strip=True)

                        # Handle nested elements like links or spans
                        if cell.find('span', class_='price-data'):
                            price_span = cell.find('span', class_='price-data')
                            price_value_span = price_span.find('span', class_='price-value')
                            price_text = price_value_span.get_text(strip=True) if price_value_span else "N/A"

                            # Store only the price without regional_prices
                            model_data[header] = {
                                'price': price_text
                            }
                        elif cell.find('a'):
                            # Handle links (e.g., model names with links)
                            link = cell.find('a')
                            link_text = link.get_text(strip=True)
                            model_data[header] = link_text
                        else:
                            model_data[header] = cell_text if cell_text else "N/A"

                    # Assign the model data to the model name key within the category
                    pricing_data[category_name][model_text] = model_data

        print("Completed scraping pricing details.")
        return pricing_data

    except TimeoutException:
        print("Timeout: Pricing section was not found within the given time.")
        return pricing_data
    except Exception as e:
        print(f"An unexpected error occurred while scraping pricing details: {e}")
        return pricing_data