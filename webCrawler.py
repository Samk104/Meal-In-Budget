# import requests
# from bs4 import BeautifulSoup
# import threading
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service

# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.edge.service import Service
# import collections
# import os
# import json
# from flask import Flask, request, render_template
# from flask import session,redirect,url_for,copy_current_request_context
# from threading import Thread
# from flask import jsonify



# app = Flask(__name__)
# app.secret_key = "MMMMMM99999"





# @app.route("/")
# def index():
#     return render_template("index.html")






# #===========================================Added route for urls==========================================
# @app.route('/get-urls')
# def get_urls():
#     visited_urls = load_visited_urls()
#     return jsonify(list(visited_urls.keys()))


# @app.route('/loading')
# def loading():
#     @copy_current_request_context
#     def process_results():
#         dish = session.get('dish')
#         zipcode = session.get('zipcode')
#         ingredients, image = get_recipe(dish)
#         length = len(ingredients)
#         stores = ["walmart","samsclub","kroger"]

#         visited_urls = load_visited_urls()   # Loading visited url's

#         threads = []
#         thread_id = 1

#         net_store_cost = collections.defaultdict(list)

#         for ingredient in ingredients:
#             for store in stores:
#                 thread = threading.Thread(target=get_price, args=(ingredient, store, zipcode, net_store_cost,visited_urls), name=str(thread_id))
#                 threads.append(thread)
#                 print(f"Thread {thread_id} created for getting price of {ingredient} at {store}")
#                 thread.start()
#                 thread_id += 1
#         for thread in threads:
#             thread.join()

#         print(net_store_cost)
#         for s,c in net_store_cost.items():
#             net_store_cost[s] = round(sum(c),2)

#         print(net_store_cost)
#         # Store the processed results in the session
#         # session['net_store_cost'] = net_store_cost
#         # session['ingredients'] = ingredients
#         # session['image'] = image
#         # session['length'] = length
#         # session['processing_complete'] = True
        
#         # Store the processed results in a file
#         with open('results.json', 'w') as f:
#             json.dump({
#                 'net_store_cost': net_store_cost,
#                 'ingredients': ingredients,
#                 'image': image,
#                 'length': length,
#                 'dish' : dish
#             }, f)
        
#         # Write a file to indicate that the processing is complete
#         with open('processing_complete.txt', 'w') as f:
#             f.write('True')

        

#     # Start the background task
#     Thread(target=process_results).start()
    

#     # Render the loading page
#     return render_template("loading.html")

# @app.route('/check_results')
# def check_results():
#     # Check if the processing is complete by checking if the file exists
#     results_ready = os.path.exists('results.json')

#     return {'results_ready': results_ready}


# @app.route('/results')
# def results():
#     # Get the session data from the file
#     with open('results.json', 'r') as f:
#         results = json.load(f)

#     net_store_cost = results.get('net_store_cost')
#     ingredients = results.get('ingredients')
#     image = results.get('image')
#     length = results.get('length')
#     dish = results.get('dish')

#     # Delete the file
#     if os.path.exists('results.json'):
#         os.remove('results.json')

#     # Render the results page with the session data
#     return render_template("results.html", net_store_cost=net_store_cost, ingredients=ingredients, image=image, dish = dish, length=length)



# # def home():
# #     return render_template('index.html')
# @app.route('/submit', methods=['POST','GET'])
# def submit():
#     # Store the form data in the session
#     session['dish'] = str(request.form['dish'])
#     session['zipcode'] = 30324

#     # Redirect to the loading page
#     return redirect(url_for('loading'))




# if __name__ == "__main__":
#     app.run(debug=True, port=8080)