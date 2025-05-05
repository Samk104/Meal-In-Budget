import logging
import requests
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from .utils import get_driver_pool, save_visited_urls, thread_safe_append
from .stores import get_store_price
from mib_app.services.utils import visited_urls_lock

logger = logging.getLogger(__name__)

STORE_CONFIG = {
    "walmart": {"url_base": "https://www.walmart.com"},
    "kroger": {"url_base": "https://www.kroger.com"},
    "samsclub": {"url_base": "https://www.samsclub.com"}
}

def get_recipe(dish: str) -> Tuple[List[str], str]:
    if not dish or not isinstance(dish, str):
        logger.error("Invalid dish name provided")
        return [], ""

    dish_query = dish.lower().replace(' ', '+')
    search_url = f"https://www.allrecipes.com/search?q={dish_query}"
    logger.info(f"Calling AllRecipes for {dish}")
    response = None
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        recipe_link = soup.find('a', {'data-ordinal': '1'})
        if not recipe_link or 'href' not in recipe_link.attrs:
            logger.warning(f"No recipe found for dish: {dish}")
            return [], ""

        recipe_url = recipe_link['href']
        logger.debug(f"Fetching recipe page: {recipe_url}")
        recipe_response = requests.get(recipe_url, headers=headers, timeout=10)
        recipe_response.raise_for_status()
        soup = BeautifulSoup(recipe_response.text, 'html.parser')

        ingredients_tags = soup.find_all('span', {'data-ingredient-name': 'true'})
        ingredients = [tag.text.split(',')[0].strip().lower() for tag in ingredients_tags if tag.text]
        if not ingredients:
            logger.warning(f"No ingredients found for recipe: {recipe_url}")
            return [], ""

        img_div = soup.find('div', {'class': 'img-placeholder'})
        img = img_div.find('img') if img_div else None
        image_url = img.get('data-src') or img.get('src', '') if img else ''
        if not image_url:
            logger.debug(f"No image found for recipe: {recipe_url}")

        return ingredients, image_url

    except requests.RequestException as e:
        logger.error(f"Failed to fetch recipe for {dish}: {e}")
        return [], ""
    except Exception as e:
        logger.error(f"Error processing recipe for {dish}: {e}")
        return [], ""

def get_prices_for_ingredient(
    ingredient: str,
    stores: List[str],
    zipcode: str,
    net_store_cost: Dict[str, List[float]],
    visited_urls: Dict[str, bool],
    driver: WebDriver,
    driver_pool  
) -> None:
    if not ingredient or not isinstance(ingredient, str):
        logger.error("Invalid ingredient provided")
        return
    if not stores or not all(store in STORE_CONFIG for store in stores):
        logger.error(f"Invalid or unsupported stores: {stores}")
        return
    if not zipcode or len(str(zipcode)) != 5:
        logger.error(f"Invalid zipcode: {zipcode}")
        return
    if not driver:
        logger.error("No WebDriver provided")
        return

    for store in stores:
        try:
            logger.info(f"Fetching price for {ingredient} from {store}")
            price = get_store_price(ingredient, store, zipcode, driver)
            if price is not None:
                thread_safe_append(net_store_cost, store, price)
                with visited_urls_lock:
                    visited_urls[STORE_CONFIG[store]["url_base"]] = True
                    save_visited_urls(visited_urls)
            else:
                logger.warning(f"No price found for {ingredient} at {store}")
                driver = driver_pool.reset_driver(driver)
                if not driver:
                    logger.error("Failed to reset driver")
                    return
        except Exception as e:
            logger.error(f"Error fetching price for {ingredient} at {store}: {e}")
            driver = driver_pool.reset_driver(driver)
            if not driver:
                logger.error("Failed to reset driver")
                return