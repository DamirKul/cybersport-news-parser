import csv
import requests

from typing import List
from bs4 import BeautifulSoup

URL_ADDRESS: str = 'https://www.cybersport.ru/rss/materials'
FILE_NAME: str = 'output.csv'


# Finds last publish date if it exists
def last_date(file: str) -> str | None:
    with open(file, 'a+', encoding='UTF-8', newline='') as f:
        f.seek(0,0)
        read_f = csv.reader(f, delimiter=' ')
        try:
            return next(read_f)[1]
        except StopIteration:
            return None


# Adds new content to the beginning of the file
def update(file: str, new_content: List[str]) -> None:
    if not new_content:
        return
    with open(file, 'r+', encoding='UTF-8', newline='') as f:
        old_content = list(csv.reader(f, delimiter=' '))
        writer = csv.writer(f, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
        f.seek(0,0)
        writer.writerows(new_content)
        writer.writerows(old_content)
        return


def parse_cybersport() -> str:
    try:
        # Get rss feed content:
        request = requests.get(URL_ADDRESS, timeout=(5, 5))
        request.raise_for_status()
        soup = BeautifulSoup(request.content, 'xml')

        # Read news to update:
        last_news = soup.find(string=last_date(FILE_NAME))
        if last_news and last_date(FILE_NAME):
            items = last_news.find_parent('item').find_previous_siblings('item')[::-1]
        else:
            items = soup.find_all('item')

        # Get necessary tags and update:
        content: List[str] = []
        for item in items:
            title = item.title.text
            date = item.pubDate.text
            link = item.link.text
            content.append([title, date, link])
        update(FILE_NAME, content)

        return 'Success'
    except requests.exceptions.RequestException as e: 
        print('Request exception occured.', e)
        return 'Failed to execute'


if __name__ == '__main__':
    print(parse_cybersport())
