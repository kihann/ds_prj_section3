import csv
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

raw_data = []
field_names = ['date', 'close_price', 'open_price', 'high_price', 'low_price', 'up', 'down', 'trading_volume']

for i in range(8, 0, -1):
    URL = 'http://finance.naver.com/item/sise_day.naver?code=005930&page={}'.format(i) # SK 하이닉스(000660), 삼성전자(005930)

    res = requests.get(URL, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    items = soup.find_all('tr')
    
    for item in reversed(items):
        
        date = item.find('span', attrs={'class':'tah p10 gray03'})
        if date:
            date = date.get_text()
        else:
            continue
        
        numbers = item.find_all('span', attrs={'class':'tah p11'})
        p0 = numbers[0].get_text()
        p1 = numbers[-4].get_text()
        p2 = numbers[-3].get_text()
        p3 = numbers[-2].get_text()
        total = numbers[-1].get_text()

        up = item.find('span', attrs={'class':'tah p11 red02'})
        down = item.find('span', attrs={'class':'tah p11 nv01'})
        if up:
            up = up.get_text().strip()
            down = 0
        elif down:
            down = '-' + down.get_text().strip()
            up = 0
        else:
            up = 0
            down = 0
        
        dict = {field_names[0]:date, field_names[1]:p0, field_names[2]:p1, field_names[3]:p2, field_names[4]:p3, field_names[5]:up, field_names[6]:down, field_names[7]:total}
        raw_data.append(dict)

#mongodb+srv://vvk:<password>@cluster0.flket.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
HOST = 'cluster0.flket.mongodb.net'
USER = 'vvk'
PASSWORD = 'vvk1004'
DATABASE_NAME = 'stock'
COLLECTION_NAME = '005930'
MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE_NAME}?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
database = client[DATABASE_NAME]
collection = database[COLLECTION_NAME]
collection.insert_many(raw_data)

with open('rawdata.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=field_names, extrasaction='ignore')
    w.writeheader()
    w.writerows(raw_data)