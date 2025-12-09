# Meal In Budget

Meal In Budget is a multithreaded web-crawler application designed to automatically gather ingredient information for user-submitted recipes and compare total costs across multiple grocery stores. The system eliminates the need to manually search various websites, enabling faster and more informed meal planning.

![Meal In Budget UI](https://github.com/Samk104/Meal-In-Budget/assets/71979346/4b496dfc-81ed-4fcb-8ed6-11a50a40196b)
![Meal In Budget Price Comparison](https://github.com/Samk104/Meal-In-Budget/assets/71979346/590f0f53-00aa-4c21-8e62-109850a42ec2)

---

## Overview

Meal planning often requires deciding what to cook, listing ingredients, and checking prices across different stores. For students and busy individuals, this process is time-consuming. Meal In Budget addresses these challenges by automating ingredient extraction and price comparison, providing users with a cost-optimized shopping overview in minutes.

---

## Features

- **Automated Ingredient Retrieval**  
  The system extracts required ingredients from the recipe input provided by the user.

- **Price Comparison Across Stores**  
  Retrieves ingredient prices from multiple grocery stores and calculates total cost estimates per store.

- **Multithreaded Web Scraping**  
  Implemented using Python’s threading module, reducing lookup time by approximately 40%.

- **Detailed Cost Breakdown**  
  Provides itemized ingredient costs and total prices per store to help users choose the most economical option.

---

## Technologies Used

<table>
  <tr>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="50" alt="Python"/><br>
      Python
    </td>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/flask/flask-original.svg" width="50" alt="Flask"/><br>
      Flask
    </td>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://app.matatika.com/assets/images/datasource/tap-beautifulsoup.png" width="50" alt="BeautifulSoup"/><br>
      BeautifulSoup
    </td>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/selenium/selenium-original.svg" width="50" alt="Selenium"/><br>
      Selenium
    </td>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Microsoft_Edge_logo_%282019%29.svg/512px-Microsoft_Edge_logo_%282019%29.svg.png?20220108180202" width="50" alt="Edge WebDriver"/><br>
      Edge WebDriver
    </td>
  </tr>
  <tr>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original.svg" width="50" alt="HTML"/><br>
      HTML
    </td>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original.svg" width="50" alt="CSS"/><br>
      CSS
    </td>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" width="50" alt="JavaScript"/><br>
      JavaScript
    </td>
    <td align="center" width="140" style="background-color:white;">
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/AJAX_logo_by_gengns.svg/256px-AJAX_logo_by_gengns.svg.png?20221015001337" width="50" alt="AJAX"/><br>
      AJAX
    </td>
  </tr>
</table>

---

## Project Summary

**Meal In Budget – Multithreaded Web Crawler**  
*Oct 2023 – Dec 2023*

- Built a web application using Python, Flask, BeautifulSoup, and Selenium that allows users to input a recipe and automatically compare total ingredient costs across local grocery stores.  
- Implemented multithreaded scraping with Python’s threading module, reducing end-to-end price lookup time by approximately 40% across ingredient–store combinations.  
- Delivered detailed per-store pricing breakdowns to help identify the most cost-effective option for purchasing complete ingredient sets.

---

## How to Run the Flask Application

Follow the steps below to set up and run the project locally.

### 1. Clone the Repository
```
git clone https://github.com/Samk104/Meal-In-Budget.git
cd Meal-In-Budget
```

### 2. Create a Virtual Environment
```
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure WebDriver

Download the appropriate Microsoft Edge WebDriver version matching your installed browser.
Place the executable in the project directory, or update the WebDriver path inside the codebase.

### 5. Run the Application
```
export FLASK_APP=run.py         # macOS / Linux
set FLASK_APP=run.py            # Windows

flask run
```

The application will be available at:

```
http://127.0.0.1:5000
```
