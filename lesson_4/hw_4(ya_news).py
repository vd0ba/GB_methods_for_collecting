# 1) Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# 2) Сложить собранные новости в БД.
# Минимум один сайт, максимум - все три


# Yandex news

import requests
from pprint import pprint
from lxml.html import fromstring
from datetime import datetime
from pymongo import MongoClient

url = "https://yandex.ru/news/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
}

ITEMS_XPATH = '//section[1]//div[contains(@class, "mg-grid__col")]'
HREF_XPATH = './/h2[contains(@class, "mg-card__title")]/a/@href'
TITLE_XPATH = './/h2[contains(@class, "mg-card__title")]/a/text()'
SOURCE_XPATH = './/span[contains(@class, "mg-card-source__source")]//a/text()'
TIME_XPATH = './/span[contains(@class, "mg-card-source__time")]/text()'

mongo_host = "localhost"
mongo_port = 27017
mongo_db = "news"
mongo_collection = "yandex_news"


class YaNews:
    def __init__(self):
        self.news_list = []

    @staticmethod
    def get_dom():
        r = requests.get(url, headers=headers)
        dom = fromstring(r.text)
        return dom

    def get_info_news(self, items):
        for item in items:
            news = {}
            news["link"] = item.xpath(HREF_XPATH)[0]
            news["title"] = item.xpath(TITLE_XPATH)[0].replace('\xa0', ' ')
            news["source"] = item.xpath(SOURCE_XPATH)[0]
            news["date"] = self.get_datetime(str(item.xpath(TIME_XPATH)[0]))
            # pprint(news)
            self.news_list.append(news)

            with MongoClient(mongo_host, mongo_port) as client:
                db = client[mongo_db]
                collection = db[mongo_collection]
                collection.update_one(
                    {
                        'title': news['title'],
                    },
                    {
                        "$set": {
                            'link': news['link'],
                            'source': news["source"],
                            'date': news["date"]
                        }
                    },
                    upsert=True,
                )

    def get_datetime(self, time):
        if len(time) >= 13:
            date_time = f'{str(datetime.now().date()-1)} {time}'
        else:
            date_time = f'{str(datetime.now().date())} {time}'
        return datetime.strptime(date_time, '%Y-%m-%d %H:%M')

    @staticmethod
    def read_db():
        with MongoClient(mongo_host, mongo_port) as client:
            db = client[mongo_db]
            collection = db[mongo_collection]
            return list(collection.find())

    def run(self):
        dom = self.get_dom()
        items = dom.xpath(ITEMS_XPATH)
        self.get_info_news(items)
        pprint(self.read_db())


if __name__ == "__main__":
    news_parser = YaNews()
    news_parser.run()

pprint()
