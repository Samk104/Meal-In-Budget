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
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.edge.service import Service
import collections
import os
import json
from flask import Flask, request, render_template
from flask import session,redirect,url_for,copy_current_request_context
from threading import Thread
from flask import jsonify



app = Flask(__name__)
app.secret_key = "MMMMMM99999"





@app.route("/")
def index():
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


    if recipe_link:
        # Find the img tag inside the figure
        img = recipe_link.find_next('img')

        if img:
            # Extract the 'data-src' or 'src' attribute, whichever is present
            image = img.get('data-src') if 'data-src' in img.attrs else img.get('src')
            print(image)
    return ing, image



def get_price(ingredient, store, zipcode, net_store_cost, visited_urls):

    ingredient = ingredient.lower().replace(' ','+')
#---------------------------WALMART----------------------------------------------------------------------------------------
    if store == "walmart":
        itemprice = 0


        # chrome_options = webdriver.ChromeOptions()

        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument("disable-blink-features=AutomationControlled")
        # driver = webdriver.Chrome(options=chrome_options)


        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument("disable-blink-features=AutomationControlled")
        edge_options.add_argument("--window-size=0,0")
        driver = webdriver.Edge(options=edge_options)
        driver.set_window_position(2200, 0)
        # Replace with the URL you want to visit
        url = "https://www." + store + ".com/search/?query=" + ingredient
        driver.get(url)

        time.sleep(5)

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
            spans = div.find('span' , {'class': 'w_iUH7'})
            items.append(float(spans.text.split('$')[1]))


        # Print the list of texts
        itemprice = round(min(items),2)
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
        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument("disable-blink-features=AutomationControlled")
        # edge_options.add_argument("--headless")
        edge_options.add_argument("--window-size=10,10")
        driver = webdriver.Edge(options=edge_options)
        driver.set_window_position(2200, 0)
        # driver.set_window_position(2000, 0)
        url = "https://www." + store + ".com/search/?query=" + ingredient
        driver.get(url)
        # print("page fetched")
        time.sleep(7)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        prices = []
        for span in soup.find_all('span', {'class': 'kds-Price-promotional-dropCaps'}):
            sup = span.find_next('sup', {'class': 'kds-Price-superscript'})
            if sup:
                price = span.text + sup.text
                prices.append(float(price))
        minprice = round(min(prices),2)
        print(f"Best price found for {ingredient.replace('+',' ')} at {store} is {minprice}\n")
        with lock:
        # update the dictionary
            net_store_cost[store].append(round(minprice,2))
        
        #Saving url
        visited_urls[url] = True
        save_visited_urls(visited_urls)
        
        driver.quit()

#---------------------------SAFEWAY----------------------------------------------------------------------------------------
    elif store == "safeway":
        itemprice = 0
        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument("disable-blink-features=AutomationControlled")
        edge_options.add_argument("--window-size=0,0")
        driver = webdriver.Edge(options=edge_options)
        driver.set_window_position(2200, 0)
        

        url = "https://www." + store + ".com/shop/search-results.html?q=" + ingredient
        
        driver.get(url)
        
        time.sleep(7)

        # Get the HTML content of the page
        html = driver.page_source
        
        soup = BeautifulSoup(html, 'html.parser')
        

        span_tags = soup.find_all('span', attrs={'data-qa': 'prd-itm-prc'})
        
        items = []
        
        # extract and print the text inside each tag
        for tag in span_tags:
            pr = tag.text.split(' ')[2][1:]
            items.append(float(pr))
        
        
        itemprice = round(min(items),2)
        print(f"Best price for {ingredient.replace('+',' ')} at safeway is {itemprice}")
        with lock:
        # update the dictionary
            net_store_cost[store].append(round(itemprice,2))
        
        #Saving url
        visited_urls[url] = True
        save_visited_urls(visited_urls)
            
        driver.quit()
#---------------------------SAM'S CLUB----------------------------------------------------------------------------------------
    elif store == "samsclub":
        itemprice = 0
        
        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument("disable-blink-features=AutomationControlled")
        edge_options.add_argument("--window-size=0,0")
        driver = webdriver.Edge(options=edge_options)
        driver.set_window_position(2200, 0)

        url = "https://www." + store + ".com/s/" + ingredient
        #https://www.samsclub.com/s/eggs

        driver.get(url)

        time.sleep(7)

        # Get the HTML content of the page
        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        # find the button and click it
        # button = driver.find_element(By.ID, 'onetrust-reject-all-handler')
        # button.click()

        span_tags = soup.find_all('span', attrs={'class': 'Price-group'})
        
        
        items = []
        
        # extract and print the text inside each tag
        for span in span_tags:
            pr=span.find('span',attrs={'class':'visuallyhidden'})
            items.append(float((pr.text.split('$')[1].split('/')[0].replace(',',''))))
        
        
        itemprice = round(min(items),2)
        print(f"Best price for {ingredient.replace('+',' ')} at Sam's Club is {itemprice}")
        
        with lock:
        # update the dictionary
            net_store_cost[store].append(round(itemprice,2))
        
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


#===========================================Added route for urls==========================================
@app.route('/get-urls')
def get_urls():
    visited_urls = load_visited_urls()
    return jsonify(list(visited_urls.keys()))


@app.route('/loading')
def loading():
    @copy_current_request_context
    def process_results():
        dish = session.get('dish')
        zipcode = session.get('zipcode')
        ingredients, image = get_recipe(dish)
        length = len(ingredients)
        stores = ["walmart","samsclub","kroger"]

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
            net_store_cost[s] = round(sum(c),2)

        print(net_store_cost)
        # Store the processed results in the session
        # session['net_store_cost'] = net_store_cost
        # session['ingredients'] = ingredients
        # session['image'] = image
        # session['length'] = length
        # session['processing_complete'] = True
        
        # Store the processed results in a file
        with open('results.json', 'w') as f:
            json.dump({
                'net_store_cost': net_store_cost,
                'ingredients': ingredients,
                'image': image,
                'length': length,
                'dish' : dish
            }, f)
        
        # Write a file to indicate that the processing is complete
        with open('processing_complete.txt', 'w') as f:
            f.write('True')

        

    # Start the background task
    Thread(target=process_results).start()
    

    # Render the loading page
    return render_template("loading.html")

@app.route('/check_results')
def check_results():
    # Check if the processing is complete by checking if the file exists
    results_ready = os.path.exists('results.json')

    return {'results_ready': results_ready}


@app.route('/results')
def results():
    # Get the session data from the file
    with open('results.json', 'r') as f:
        results = json.load(f)

    net_store_cost = results.get('net_store_cost')
    ingredients = results.get('ingredients')
    image = results.get('image')
    length = results.get('length')
    dish = results.get('dish')

    # Delete the file
    if os.path.exists('results.json'):
        os.remove('results.json')

    # Render the results page with the session data
    return render_template("results.html", net_store_cost=net_store_cost, ingredients=ingredients, image=image, dish = dish, length=length)



# def home():
#     return render_template('index.html')
@app.route('/submit', methods=['POST','GET'])
def submit():
    # Store the form data in the session
    session['dish'] = str(request.form['dish'])
    session['zipcode'] = 30324

    # Redirect to the loading page
    return redirect(url_for('loading'))




if __name__ == "__main__":
    app.run(debug=True, port=8080)