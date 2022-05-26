import time
import requests
from pprint import pprint

from lxml.html import fromstring
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


mongo_host = "localhost"
mongo_port = 27017
mongo_db = "vk"
mongo_collection = "group_posts"

DRIVER_PATH = "../selenium_drivers/chromedriver.exe"
URL = "https://vk.com/tokyofashion"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
}
# STR_SEARCH = 'Желтый'
STR_SEARCH = input("Введите слово для поиска: ")
i_xpath = "//div[contains(@class, 'all own post')]"
i_date = ".//div[contains(@class, 'post_date')]//span[@class = 'rel_date']/text()"

r = requests.get(URL, headers=HEADERS)
dom = fromstring(r.text, 'html')
items = dom.xpath(i_xpath)

# pprint(items)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(DRIVER_PATH, options=options)
driver.get(URL)
time.sleep(1.5)

#
bottom_page = driver.find_element_by_id("page_search_posts")
actions = ActionChains(driver)
actions.move_to_element(bottom_page).perform()
close_reg = driver.find_element_by_class_name("UnauthActionBox__close")
close_reg.click()

for i in range(3):
    time.sleep(3)
    last_post = driver.find_elements_by_class_name("post--withPostBottomAction")
    if not last_post:
        break
    actions.move_to_element(last_post[-1]).perform()

time.sleep(1)
cursor = driver.find_element_by_id("wall_tabs")
actions.move_to_element(cursor).perform()

time.sleep(1)
search = driver.find_element_by_css_selector("a.ui_tab_search")
search.click()

time.sleep(1)
search_input = driver.find_element_by_id("wall_search")
search_input.send_keys(STR_SEARCH)
search_input.send_keys(Keys.ENTER)

time.sleep(1)
for item in items:
    info_posts = {}
    info_posts['Data'] = item.xpath(i_date)[0].replace('\xa0', ' ')
    info_posts['Text'] = item.xpath(".//div[@class='wall_post_text']/text()")[0]
    info_posts['Link'] = 'https://vk.com' + item.xpath(".//a[@class='post_link']/@href")[0]
    # info_posts['Link_img'] = item.xpath("")
    info_posts['Like'] = item.xpath(".//div[contains(@class, 'PostButtonReactions__title')]")[0].text
    info_posts['Repost'] = item.xpath(".//div[contains(@class, '_share')]//@data-count")[0]
    info_posts['Views'] = item.xpath(".//span[@class= '_views']/text()")[0]
    # pprint(info_posts)
time.sleep(2)

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

driver.quit()

with MongoClient(mongo_host, mongo_port) as client:
    db = client[mongo_db]
    collection = db[mongo_collection]
    collection.update_one(
        {
            'Link': info_posts['Link'],
        },
        {
            "$set": {
                'Date': info_posts['Data'],
                'Text': info_posts['Text'],
                'likes': info_posts['Like'],
                'Repost': info_posts['Repost'],
                'Views': info_posts['Views']
            }
        },
        upsert=True)
    f_d = list(collection.find())
    pprint(f_d)
