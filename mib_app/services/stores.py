from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
import time
import re
from typing import Optional
from .utils import get_driver_pool

logger = logging.getLogger(__name__)

def get_store_price(ingredient: str, store: str, zipcode: str, driver: WebDriver, retries: int = 1) -> Optional[float]:
    if not driver:
        logger.error("No driver provided")
        return None

    driver_pool = get_driver_pool()
    ingredient_query = ingredient.replace(' ', '+')
    url = ""
    prices = []
    
    for attempt in range(retries + 1):
        logger.info(f"Attempt {attempt + 1}/{retries + 1}: Searching for {ingredient} in {store}...")
        
        try:
            try:
                driver.execute_script("return true")
                logger.debug("Driver is healthy")
            except TimeoutException as e:
                logger.warning(f"Driver health check failed: {e}")
                continue

            if store == "walmart":
                url = f"https://www.walmart.com/search/?query={ingredient_query}"
                logger.debug(f"Navigating to Walmart URL: {url}")
                start_time = time.time()
                driver.get(url)
                logger.debug(f"Walmart page loaded in {time.time() - start_time:.2f} seconds")

                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@data-automation-id="product-price"]'))
                )


                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                price_spans = soup.find_all('span', class_='w_iUH7')

                prices = []
                for span in price_spans:
                    text = span.get_text(strip=True)
                    match = re.search(r'\$(\d+\.\d{2})', text)
                    if match:
                        try:
                            price = float(match.group(1))
                            prices.append(price)
                        except ValueError:
                            logger.warning(f"❌ Failed to parse price from text: {text}")

                if prices:
                    final_price = round(min(prices), 2)
                    logger.info(f"✅ Final price extracted: ${final_price}")
                    return final_price
                else:
                    logger.warning("❌ No valid prices found in w_iUH7 spans")
                    return None

            
            elif store == "kroger":
                url = f"https://www.kroger.com/search?query={ingredient_query}&searchType=default_search"
                logger.debug(f"Navigating to Kroger URL: {url}")
                start_time = time.time()
                driver.get(url)
                logger.debug(f"Kroger page loaded in {time.time() - start_time:.2f} seconds")

                # Wait for <data> price elements to load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'data[data-testid="cart-page-item-unit-price"]'))
                )

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Find structured price elements
                price_tags = soup.find_all('data', {'data-testid': 'cart-page-item-unit-price'})
                logger.debug(f"Kroger price <data> tags found: {len(price_tags)}")

                for tag in price_tags:
                    try:
                        price_str = tag.get('value')
                        if price_str:
                            price = float(price_str)
                            prices.append(price)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Couldn't parse price from tag: {tag} | Error: {e}")

            
            if store == "samsclub":
                url = f"https://www.samsclub.com/s/{ingredient_query}"
                logger.debug(f"Navigating to Sam's Club URL: {url}")
                start_time = time.time()
                driver.get(url)
                logger.debug(f"Sam's Club page loaded in {time.time() - start_time:.2f} seconds")

                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.Price-group, span.price, div.sc-price-card__price'))
                )
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                price_spans = soup.select('span.Price-group, span.price, div.sc-price-card__price')
                logger.debug(f"Sam's Club price spans: {[span.text.strip() for span in price_spans]}")
                
                for span in price_spans:
                    text = span.text.strip()
                    if '$' in text:
                        try:
                            match = re.search(r'\$(\d+\.\d{2})(?:/[^0-9]|$)', text.split('/')[0].replace(',', ''))
                            if match:
                                price = float(match.group(1))
                                prices.append(price)
                            else:
                                logger.warning(f"Could not parse price: {text}")
                        except (AttributeError, ValueError) as e:
                            logger.warning(f"Error parsing price '{text}': {e}")
            
            return round(min(prices), 2) if prices else None

        except TimeoutException as e:
            logger.error(f"Attempt {attempt + 1} failed: Timeout loading {url}: {e}")
            if attempt < retries:
                logger.info("Retrying...")
                driver = driver_pool.reset_driver(driver)
                if not driver:
                    logger.error("Failed to reset driver")
                    return None
                time.sleep(2)
                continue
            logger.warning(f"No price found for {ingredient} at {store}")
            return None
        except WebDriverException as e:
            logger.error(f"Attempt {attempt + 1} failed: WebDriver error for {url}: {e}")
            if attempt < retries:
                logger.info("Retrying...")
                driver = driver_pool.reset_driver(driver)
                if not driver:
                    logger.error("Failed to reset driver")
                    return None
                time.sleep(2)
                continue
            logger.warning(f"No price found for {ingredient} at {store}")
            return None
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: Unexpected error for {ingredient} in {store}: {e}")
            return None