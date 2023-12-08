import csv
import requests

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, Session
from typing import List
from bs4 import BeautifulSoup, ResultSet

URL_ADDRESS: str = 'https://www.cybersport.ru/rss/materials'
FILE_NAME: str = 'output.csv'

Base = declarative_base()


class NewsModel(Base):
    __tablename__ = 'news'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str] = mapped_column()
    pub_date: Mapped[str] = mapped_column()
    link: Mapped[str] = mapped_column()


# Find last publish date if it exists
def check_file_status(file: str) -> str | None:
    try:
        with open(file, encoding='UTF-8', newline='') as f:
            read_f = list(csv.reader(f, delimiter=' '))
            return read_f[-1][1]
    except FileNotFoundError:
        print('Output file does not exist. Creating a new file.')
        return
    except IndexError:
        print('File is empty, getting all content available.')
        return


# Find required item tags
def get_soup_content(soup: BeautifulSoup, last_date: str | None) -> ResultSet:
    last_news = soup.find(string=last_date) if last_date else None
    try:
        if last_news:
            return last_news.find_parent('item').find_previous_siblings('item')
        return soup.find_all('item')[::-1]
    except AttributeError:
        print("Error: can't find 'item' tag in parsed content.")
        return []


# Wrap item tags in list
def get_list_result(items: ResultSet, engine: Engine) -> List[str]:
    content: List[str] = []
    with Session(engine) as session:
        with session.begin():
            NewsModel.metadata.create_all(engine)
            for item in items:
                title = item.title.text if item.title else None
                date = item.pubDate.text if item.pubDate else None
                link = item.link.text if item.link else None
                content.append([title, date, link])
                session.add(NewsModel(title=title, pub_date=date, link=link))
    return content


# Append new content to the file
def update_file_content(file: str, new_content: List[str]) -> None:
    if not new_content:
        return
    try:
        with open(file, 'a', encoding='UTF-8', newline='') as f:
            writer = csv.writer(f, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(new_content)
            return
    except OSError as e:
        print('Error while working with file:', e)
        return


def parse_cybersport() -> None:
    try:
        request = requests.get(URL_ADDRESS, timeout=(5, 5))
        request.raise_for_status()
        soup = BeautifulSoup(request.content, 'xml')
        engine = create_engine("sqlite+pysqlite:///cybernews.db")

        check = check_file_status(FILE_NAME)
        items = get_soup_content(soup, check)
        content = get_list_result(items, engine)
        update_file_content(FILE_NAME, content)
        return
    except requests.exceptions.RequestException as e: 
        print('Request exception occured.', e)
        return


if __name__ == '__main__':
    parse_cybersport()
