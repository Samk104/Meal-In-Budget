import random
import threading
import time
import logging
import json
import os
from queue import Queue
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

visited_urls_lock = threading.Lock()

class DriverPool:
    def __init__(self, min_drivers: int = 2, max_drivers: int = 4):
        self.min_drivers = min_drivers
        self.max_drivers = max_drivers
        self.active_drivers = 0
        self.lock = threading.Lock()
        self.drivers = Queue()
        for _ in range(self.min_drivers):
            driver = self._create_driver()
            if driver:
                self.drivers.put(driver)
                self.active_drivers += 1
        logger.info(f"Initialized driver pool with {self.min_drivers} min, {self.max_drivers} max drivers")

    def _create_driver(self) -> Optional[webdriver.Edge]:
        try:
            logger.info("🛠️ Starting Edge driver creation")
            options = EdgeOptions()
            # options.add_argument('--headless')
            # options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91"
            options.add_argument(f'user-agent={user_agent}')

            
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)

            
            options.add_argument(f'--window-size={random.randint(1200, 1600)},{random.randint(800, 1000)}')

            
            options.add_argument('--enable-javascript')
            options.add_argument('--disable-infobars')

            
            driver = webdriver.Edge(options=options)
            driver.set_page_load_timeout(30)

            
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logger.error(f"Driver creation failed: {e}")
            return None

    def is_driver_healthy(self, driver: webdriver.Edge) -> bool:
        try:
            driver.title  
            return True
        except:
            return False

    def get_driver(self) -> Optional[webdriver.Edge]:
        start_time = time.time()
        while time.time() - start_time < 30:
            with self.lock:
                if not self.drivers.empty():
                    driver = self.drivers.get()
                    logger.info(f"Pulled driver from pool. Active: {self.active_drivers}, Queue: {self.drivers.qsize()}")
                    if self.is_driver_healthy(driver):
                        logger.info("Driver passed health check")
                        return driver
                    else:
                        logger.warning("❌ Driver failed health check. Quitting and discarding.")
                        self.active_drivers -= 1
                        driver.quit()
                        continue

                if self.active_drivers < self.max_drivers:
                    logger.info(f"Pool not full (Active: {self.active_drivers}/{self.max_drivers}). Creating new driver...")
                    self.active_drivers += 1  
                    driver = self._create_driver()
                    if driver:
                        logger.info(f"✅ New driver created. Active drivers now: {self.active_drivers}")
                        return driver
                    else:
                        self.active_drivers -= 1  
                        logger.error("Failed to create new driver")
                else:
                    logger.info(f"Pool at capacity ({self.active_drivers}/{self.max_drivers}). Waiting...")

            time.sleep(0.5)

        logger.warning(f"No drivers available after 30s wait. Active: {self.active_drivers}, Queue: {self.drivers.qsize()}")
        return None

    def release_driver(self, driver: webdriver.Edge):
        with self.lock:
            if self.is_driver_healthy(driver):
                self.drivers.put(driver)
                logger.debug("Driver released back to pool")
            else:
                logger.warning("Driver unhealthy on release, discarding")
                self.active_drivers -= 1
                driver.quit()
    
    def reset_driver(self, old_driver: webdriver.Edge) -> Optional[webdriver.Edge]:
        with self.lock:
            try:
                if old_driver:
                    old_driver.quit()
                    self.active_drivers -= 1
            except Exception as e:
                logger.warning(f"Error quitting old driver: {e}")

            driver = self._create_driver()
            if driver:
                self.active_drivers += 1
                logger.info("Driver successfully reset")
            else:
                logger.warning("Failed to reset driver")
            return driver


    def close(self):
        with self.lock:
            while not self.drivers.empty():
                driver = self.drivers.get()
                driver.quit()
            self.active_drivers = 0
            logger.info("All drivers closed and pool cleared")


_driver_pool: Optional[DriverPool] = None

def init_driver_pool(min_drivers: int = 2, max_drivers: int = 4):
    global _driver_pool
    if _driver_pool is None:
        _driver_pool = DriverPool(min_drivers, max_drivers)
        logger.info("Global driver_pool initialized")

def get_driver_pool() -> DriverPool:
    if _driver_pool is None:
        raise RuntimeError("Driver pool not initialized. Call init_driver_pool() in run.py.")
    return _driver_pool

def thread_safe_append(dictionary: Dict[str, List[float]], key: str, value: float):
    lock = threading.Lock()
    with lock:
        if key not in dictionary:
            dictionary[key] = []
        dictionary[key].append(value)

def load_visited_urls(path: str = "visited_urls.json") -> Dict[str, bool]:
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_visited_urls(data: Dict[str, bool], path: str = "visited_urls.json"):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def safe_write_results(path: str, results: Dict):
    temp_path = path + ".tmp"
    with open(temp_path, 'w') as f:
        json.dump(results, f, indent=2)
    os.replace(temp_path, path)