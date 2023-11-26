import csv
import requests

from typing import List
from bs4 import BeautifulSoup, ResultSet

URL_ADDRESS: str = 'https://www.cybersport.ru/rss/materials'
FILE_NAME: str = 'output.csv'


# Find last publish date if it exists
def check_file_status(file: str) -> str | None:
    try:
        with open(file, encoding='UTF-8', newline='') as f:
            read_f = list(csv.reader(f, delimiter=' '))
            print(f'Latest news publish date is {read_f[-1][1]}, looking for update.')
            return read_f[-1][1]
    except FileNotFoundError:
        print('Output file does not exist. Creating a new file.')
    except IndexError:
        print('File is empty, getting all content available.')
    return None


# Find required item tags
def get_soup_content(soup: BeautifulSoup, last_date: str | None) -> ResultSet:
    last_news = soup.find(string=last_date) if last_date else None
    if last_news:
        return last_news.find_parent('item').find_previous_siblings('item')
    return soup.find_all('item')[::-1]


# Wrap item tags in list
def get_list_result(items: ResultSet) -> List[str]:
    content: List[str] = []
    for item in items:
        title = item.title.text if item.title else None
        date = item.pubDate.text if item.pubDate else None
        link = item.link.text if item.link else None
        content.append([title, date, link])
    return content


# Append new content to the file
def update_file_content(file: str, new_content: List[str]) -> str:
    if not new_content:
        return 'Currently no content to add.'
    with open(file, 'a', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(new_content)
        return f'{len(new_content)} new lines added to the file!'


def parse_cybersport() -> str:
    try:
        request = requests.get(URL_ADDRESS, timeout=(5, 5))
        request.raise_for_status()
        soup = BeautifulSoup(request.content, 'xml')

        check = check_file_status(FILE_NAME)
        items = get_soup_content(soup, check)
        content = get_list_result(items)
        return update_file_content(FILE_NAME, content)
    except requests.exceptions.RequestException as e: 
        return f'Request exception occured. {e}'


if __name__ == '__main__':
    print(parse_cybersport())
