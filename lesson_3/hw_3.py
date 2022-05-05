import json
import requests
import time
from pprint import pprint

from pymongo import DESCENDING, MongoClient
from bs4 import BeautifulSoup as bs

mongo_host = "localhost"
mongo_port = 27017
mongo_db = "vacancy_list"
mongo_collection = "hh_vacancy"

url = 'https://hh.ru/search/vacancy'

params = {
    'text': '',
    'page': 0,
    # 'area': '2073'
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}

file_vacancy = 'vacancy.json'


class HHScraper:
    def __init__(self, url, vacancy, page):
        self.url = url
        self.vacancy = vacancy
        self.page_number = page
        self.headers = headers
        self.params = self.create_params()
        # self.vacancy_list = []

    def create_params(self):
        params['text'] = self.vacancy
        return params

    def get_html_string(self, url, params):
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
        except Exception as e:
            time.sleep(2)
            print(e)
            return None
        return response.text

    @staticmethod
    def get_dom(html_string):
        return bs(html_string, "html.parser")

    def get_info_vacancy(self, soup):
        vacancy_elements = soup.find_all('div', class_='vacancy-serp-item__layout')
        for element in vacancy_elements:
            vacancy = {}
            name_vacancy = element.find('a', class_='bloko-link').text.strip()
            salary = element.find('span', class_='bloko-header-section-3')
            min_salary, max_salary, currency = self.get_salary(salary)
            town = element.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text
            company = element.find('a', {'class': 'bloko-link bloko-link_kind-tertiary'}).text
            link = element.find('a', class_='bloko-link').get('href')
            vacancy['Название вакансии'] = name_vacancy
            vacancy['Город'] = town
            vacancy['Работодатель'] = company
            vacancy['Ссылка'] = link
            vacancy['Источник'] = self.url
            vacancy['Мин. зарплата'] = min_salary
            vacancy['Макс. зарплата'] = max_salary
            vacancy['Валюта'] = currency
            # self.vacancy_list.append(vacancy)
            self.insert_db(vacancy)

    def insert_db(self, vacancy):
        with MongoClient(mongo_host, mongo_port) as client:
            db = client[mongo_db]
            collection = db[mongo_collection]
            if not list(collection.find(vacancy)):
                collection.insert_one(vacancy)

    @staticmethod
    def get_salary(salary):
        if salary:
            salary = salary.text.replace('\u202f', '')
            salary = salary.split(' ')
            if salary[0] == 'от':
                min_salary = salary[1]
                max_salary = None
                currency = salary[2]
            else:
                if salary[0] == 'до':
                    min_salary = None
                    max_salary = salary[1]
                    currency = salary[2]
                else:
                    min_salary = salary[0]
                    max_salary = salary[2]
                    currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            currency = None
        return min_salary, max_salary, currency

    def next_button(self, soup):
        return soup.find('a', class_='bloko-button')

    def run(self):
        for page in range(0, self.page_number):
            print(f'Получаем страницу {page + 1}')
            self.params['page'] = page
            response = self.get_html_string(url, params)
            soup = self.get_dom(response)
            self.get_info_vacancy(soup)
            if self.next_button(soup) is None:
                print('Страниц больше нет...')
                break
        # return self.vacancy_list

    @staticmethod
    def save_info(data, file):
        with open(file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f'Вакансии записаны в файл {file}.')


def print_mongo_docs(cursor):
    for doc in cursor:
        pprint(doc)


def find_salary():
    in_salary = int(input('Введите размер зарплаты: '))
    # in_curr_salary = input('Введите валюту зарплаты: ')
    with MongoClient(mongo_host, mongo_port) as client:
        db = client[mongo_db]
        collection = db[mongo_collection]
        cursor = collection.find({
            # "currency": in_curr_salary,
            "$or": [{"Макс. зарплата": {"$gt": in_salary}}, {"Макс. зарплата": None}]
        }).sort("max_salary", DESCENDING)
        print_mongo_docs(cursor)


if __name__ == "__main__":
    vacancy = input("Введите название вакансии: ")
    page_number = int(input("Введите количество страниц: "))
    scraper = HHScraper(url, vacancy, page_number)
    scraper.run()
    # data_vacancy = scraper.run()
    # scraper.save_info(data_vacancy, file_vacancy)
    find_salary()
