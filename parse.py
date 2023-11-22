import csv

from bs4 import BeautifulSoup
import requests

URL_ADDRESS = 'https://www.cybersport.ru/rss/materials'


def parse_cybersport() -> None:
    try:
        request = requests.get(URL_ADDRESS, timeout=(5, 5))
        request.raise_for_status()
        soup = BeautifulSoup(request.content, 'xml')
        items = soup.find_all('item')

        with open('output.csv', 'w', encoding='UTF-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                quoting=csv.QUOTE_MINIMAL)

            for item in items:
                title = item.title.text
                date = item.pubDate.text
                link = item.link.text
                writer.writerow([title, date, link])
        
        print('Success!')
    except requests.exceptions.HTTPError as errh:
        print(errh.args[0])
    except requests.exceptions.ConnectTimeout as errct:
        print(errct.args[0])
    except requests.exceptions.ReadTimeout as errrt:
        print(errrt.args[0])
    except requests.exceptions.RequestException: 
        print('Request exception occured.')


if __name__ == '__main__':
    parse_cybersport()
