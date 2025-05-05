import os, json

def load_visited_urls():
    if os.path.exists('visited_urls.json'):
        with open('visited_urls.json', 'r') as f:
            return json.load(f)
    return {}

def save_visited_urls(urls):
    with open('visited_urls.json', 'w') as f:
        json.dump(urls, f)
