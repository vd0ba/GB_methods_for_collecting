# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import json
import requests


def get_name():
    name_user = input('Введите имя пользователя GitHub: ')
    return name_user


def get_rep_user(name_user: str):
    url = f"https://api.github.com/users/{name_user}/repos"
    response = requests.get(url)
    return response.json()


def get_names(response):
    reps_name = []
    for i in response:
        reps_name.append(i['name'])
    return reps_name


def write_json(reps_name, filename):
    with open(filename, "w") as f:
        json.dump(reps_name, f, indent=2)


user_name = get_name()
json_data = get_rep_user(user_name)
# print(json_data)
reps_name = get_names(json_data)
# print(reps_name)
write_json(reps_name, 'user_reps.json')
