from bs4 import BeautifulSoup
import requests
import csv

url = requests.get('https://www.cybersport.ru/rss/materials')

if url.status_code != 200:
    raise Exception(f'Error code {url.status_code}')


soup = BeautifulSoup(url.content, 'xml')
items = soup.find_all('item')


with open('output.csv', 'w', encoding='UTF-8', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
    
    for item in items:

        title = item.title.text
        date = item.pubDate.text
        link = item.link.text
        
        writer.writerow([title, date, link])
