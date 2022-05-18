# 1) Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# 2) Сложить собранные новости в БД.
# Минимум один сайт, максимум - все три

# News.mail.ru

import requests
from lxml.html import fromstring
from pprint import pprint
from datetime import datetime
from pymongo import MongoClient

mongo_host = "localhost"
mongo_port = 27017
mongo_db = "news"
mongo_collection = "news_mail_ru"

url = 'https://news.mail.ru/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
}

ITEMS_XPATH = "//div[contains(@class, 'daynews__item')]"
TITLE_PATH = ".//span[contains(@class, 'photo__title_new')]/text()"
LINK_PATH = ".//a/@href"


def get_first_elem_or_none(arr):
    # если непустой список
    if arr:
        return arr[0]
    return None


news_list = []
r = requests.get(url, headers=headers)
dom = fromstring(r.text)
items = dom.xpath(ITEMS_XPATH)
for item in items:
    news = {}
    news['title'] = get_first_elem_or_none(item.xpath(TITLE_PATH)).replace('\xa0', ' ')
    news['link'] = get_first_elem_or_none(item.xpath(LINK_PATH))
    r1 = requests.get(news['link'], headers=headers)
    dom1 = fromstring(r1.text)
    items1 = dom1.xpath("//div[contains(@class, 'breadcrumbs')]")
    for item1 in items1:
        news['source'] = item1.xpath(".//a/span/text()")[0]
        news['date'] = item1.xpath("//span[@datetime]/@datetime")[0]
    news_list.append(news)
    pprint(news)

# class MailNews():
#     def __init__(self):
#         self.news_list = []
#
#     def get_first_elem_or_none(arr):
#         # если непустой список
#         if arr:
#             return arr[0]
#         return None
#
#     @staticmethod
#     def get_dom():
#         r = requests.get(url, headers=headers)
#         dom = fromstring(r.text)
#         return dom
#
#     def get_info_news(self, items):
#         for item in items:
#             news = {}
#             news['title'] = self.get_first_elem_or_none(item.xpath(TITLE_PATH)).replace('\xa0', ' ')
#             news['link'] = self.get_first_elem_or_none(item.xpath(LINK_PATH))
#             r1 = requests.get(news['link'], headers=headers)
#             dom1 = fromstring(r1.text)
#             items1 = dom1.xpath("//div[contains(@class, 'breadcrumbs')]")
#             for item1 in items1:
#                 news['source'] = item1.xpath(".//a/span/text()")[0]
#                 news['date'] = item1.xpath("//span[@datetime]/@datetime")[0]
#             self.news_list.append(news)
#             pprint(news)
#
#             with MongoClient(mongo_host, mongo_port) as client:
#                 db = client[mongo_db]
#                 collection = db[mongo_collection]
#                 collection.update_one(
#                     {
#                         'title': news['title'],
#                     },
#                     {
#                         "$set": {
#                             'link': news['link'],
#                             'source': news["source"],
#                             'date': news["date"]
#                         }
#                     },
#                     upsert=True,
#                 )
#
#     @staticmethod
#     def read_db():
#         with MongoClient(mongo_host, mongo_port) as client:
#             db = client[mongo_db]
#             collection = db[mongo_collection]
#             return list(collection.find())
#
#     def run(self):
#         dom = self.get_dom()
#         items = dom.xpath(ITEMS_XPATH)
#         self.get_info_news(items)
#         pprint(self.news_list)
#         # pprint(self.read_db())
#
#
# if __name__ == "__main":
#     news_parser = MailNews()
#     news_parser.run()
