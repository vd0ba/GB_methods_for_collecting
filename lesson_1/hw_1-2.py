# Зарегистрироваться на https://openweathermap.org/api и написать
# функцию, которая получает погоду в данный момент для города,
# название которого получается через input.
# https://openweathermap.org/current

import json
import requests

import requests


def get_city():
    city = input("Введите название города: ")
    return city


def get_api():
    api = 'd961d6e5b1edd781aa32143d8dd87fb7'
    # По правильному здесь должны быть ссылка на ключ из файла .env, но он у меня пустой и не открывается
    return api


def get_weath(city, api):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}'
    response = requests.get(url).json()
    return response


def get_weather(response):
    print(f"В городе {response['name']} {round(float(response['main']['temp']) - 273)} градусов по Цельсию")


city = get_city()
response = get_weath(city, get_api())
get_weather(response)
