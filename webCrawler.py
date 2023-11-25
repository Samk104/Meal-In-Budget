import requests
from bs4 import BeautifulSoup
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import collections
import os
import json
from flask import Flask, request, render_template, flash


app = Flask(__name__)
app.secret_key = "MMMMMM99999"

@app.route("/")
def index():
    flash("Whats your name?")
    return render_template("index.html")


lock = threading.Lock()

def get_recipe(dish):
    dish = dish.lower().replace(' ', '+')
    url = "https://www.allrecipes.com/search?q=" + dish
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the URL of the first recipe in the search results
    recipe_link = soup.find('a', {'id': 'mntl-card-list-items_1-0'})
    if recipe_link is None:
        print("Could not find a recipe for the dish. Please check for typos!")
        return []
    else:
        href = recipe_link['href']
        # print(href)

    recipe_url = recipe_link['href']

    # Navigate to the recipe page and parse it
    response = requests.get(recipe_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the ingredients from the recipe page
    ingredients = soup.find_all('span', attrs={'data-ingredient-name': 'true'})
    ing=[]
    for ingredient in ingredients:
        ingredient = ingredient.text.split(',')[0]
        # print(ingredient)
        ing.append(ingredient)
    print(ing)

    return ing



def get_price(ingredient, store, zipcode, net_store_cost, visited_urls):

    ingredient = ingredient.lower().replace(' ','+')
#---------------------------WALMART----------------------------------------------------------------------------------------
    if store == "walmart":
        itemprice = 0


        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=chrome_options)

        # Replace with the URL you want to visit
        url = "https://www." + store + ".com/search/?query=" + ingredient
        driver.get(url)

        time.sleep(8)

        # Get the HTML content of the page
        html = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all div elements with a data-automation-id attribute of 'product-price'
        divs = soup.find_all('div', {'data-automation-id': 'product-price'})

        # Initialize an empty list to store the text
        items = []

        # Loop through each div and find the span element within it
        for div in divs:
            # print(div)
            spans = div.find_all('span')
         # If there are at least two span elements, append the text of the second one to the list
            if len(spans) >= 2:

                items.append(float(spans[2].text +"." +spans[3].text))

        # Print the list of texts
        itemprice += min(items)
        print(f"Best price for {ingredient.replace('+',' ')} at Walmart is {itemprice}")
        
        with lock:
        # update the dictionary
            net_store_cost[store].append(itemprice)
        
        #Saving url
        visited_urls[url] = True
        save_visited_urls(visited_urls)

        # Close the browser
        driver.quit()
#---------------------------KROGER----------------------------------------------------------------------------------------
    elif store == "kroger":
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=chrome_options)
        url = "https://www." + store + ".com/search/?query=" + ingredient
        driver.get(url)
        # print("page fetched")
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        prices = []
        for span in soup.find_all('span', {'class': 'kds-Price-promotional-dropCaps'}):
            sup = span.find_next('sup', {'class': 'kds-Price-superscript'})
            if sup:
                price = span.text + sup.text
                prices.append(float(price))
        minprice = min(prices)
        print(f"Best price found for {ingredient.replace('+',' ')} at {store} is {minprice}\n")
        with lock:
        # update the dictionary
            net_store_cost[store].append(minprice)
        
        #Saving url
        visited_urls[url] = True
        save_visited_urls(visited_urls)
        
        driver.quit()

#---------------------------SAFEWAY----------------------------------------------------------------------------------------
    elif store == "safeway":
        itemprice = 0
       
        
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=chrome_options)
        

        url = "https://www." + store + ".com/shop/search-results.html?q=" + ingredient
        
        driver.get(url)
        
        time.sleep(8)

        # Get the HTML content of the page
        html = driver.page_source
        
        soup = BeautifulSoup(html, 'html.parser')
        

        span_tags = soup.find_all('span', attrs={'data-qa': 'prd-itm-prc'})
        
        items = []
        
        # extract and print the text inside each tag
        for tag in span_tags:
            pr = tag.text.split(' ')[2][1:]
            items.append(float(pr))
        
        
        itemprice = min(items)
        print(f"Best price for {ingredient.replace('+',' ')} at safeway is {itemprice}")
        with lock:
        # update the dictionary
            net_store_cost[store].append(itemprice)
        
        #Saving url
        visited_urls[url] = True
        save_visited_urls(visited_urls)
            
        driver.quit()
#---------------------------SAM'S CLUB----------------------------------------------------------------------------------------
    elif store == "samsclub":
        itemprice = 0
        
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=chrome_options)
        

        url = "https://www." + store + ".com/s/" + ingredient
        #https://www.samsclub.com/s/eggs
        
        driver.get(url)
        
        time.sleep(8)

        # Get the HTML content of the page
        html = driver.page_source
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # find the button and click it
        # button = driver.find_element(By.ID, 'onetrust-reject-all-handler')
        # button.click()

        span_tags = soup.find_all('span', attrs={'class': 'visuallyhidden'})
        
        
        items = []
        
        # extract and print the text inside each tag
        for span in soup.find_all('span', {'class': 'Price-characteristic'}):
            span2 = span.find_next('span', {'class': 'Price-mantissa'})
            if span2:
                price = float(span.text + '.' + span2.text)
                items.append(price)
        
        
        itemprice = min(items)
        print(f"Best price for {ingredient.replace('+',' ')} at Sam's Club is {itemprice}")
        
        with lock:
        # update the dictionary
            net_store_cost[store].append(itemprice)
        
        #Saving url
        visited_urls[url] = True
        save_visited_urls(visited_urls)
        
        driver.quit()

#------------------------------------------------------SAVING VISITED LINKS------------------------------------------------------------>
def load_visited_urls():
    if os.path.exists('visited_urls.json'):
        with open('visited_urls.json', 'r') as f:
            return json.load(f)
    else:
        return {}

def save_visited_urls(urls):
    with open('visited_urls.json', 'w') as f:
        json.dump(urls, f)




# def home():
#     return render_template('index.html')
@app.route('/submit', methods=['POST','GET'])
def submit():
    dish = str(request.form['dish'])
    flash("Hi "+ dish)
    # dish = input("Enter a dish: ")
   
    # zipcode = request.form.get('zipcode')
    zipcode = 30324
    ingredients = get_recipe(dish)
    stores = ["walmart" , "safeway", "samsclub","kroger"]
  
    visited_urls = load_visited_urls()   # Loading visited url's
    
    threads = []
    thread_id = 1
    
    net_store_cost = collections.defaultdict(list)
    
    for ingredient in ingredients:
        for store in stores:
            thread = threading.Thread(target=get_price, args=(ingredient, store, zipcode, net_store_cost,visited_urls), name=str(thread_id))
            threads.append(thread)
            print(f"Thread {thread_id} created for getting price of {ingredient} at {store}")
            thread.start()
            thread_id += 1
    for thread in threads:
        thread.join()
    
    print(net_store_cost)
    for s,c in net_store_cost.items():
        net_store_cost[s] = sum(c)
    
    print(net_store_cost)
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)