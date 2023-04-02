from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from datetime import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")

url = 'https://store.steampowered.com/charts/mostplayed'

#driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver = webdriver.Chrome('./chromedriver', options=chrome_options)
driver.get(url)
WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CLASS_NAME, "weeklytopsellers_GameName_1n_4-")))

soup = BeautifulSoup(driver.page_source, 'html.parser')

titles = soup.find_all('div', {'class': 'weeklytopsellers_GameName_1n_4-'})
current = soup.find_all('td', {'class': 'weeklytopsellers_ConcurrentCell_3L0CD'})
peak_today = soup.find_all('td', {'class': 'weeklytopsellers_PeakInGameCell_yJB7D'})

driver.close()

client = MongoClient('mongodb+srv://sean:bu_final@cluster0.pvuhuo1.mongodb.net/?retryWrites=true&w=majority')
db = client['Steam_Data']
collection = db['Current_Players']

date = datetime.utcnow()
for i in range(0, len(titles)):
    collection.insert_one({
        'Updated': date,
        'Data':
        {
            'Title': titles[i].text,
            'Current': current[i].text,
            'Peak_today': peak_today[i].text
        }
    })
