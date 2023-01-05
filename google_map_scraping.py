from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
import csv
import time
import os
import threading
import re

import mysql.connector


class Restaurant:
    def __init__(self, name, address, website='N/A', phone_number='N/A', rating='N/A',
                 reviews='N/A', image='N/A', pricing='N/A', category='N/A', timing='N/A', description='N/A', servicing='N/A'):
        self.name = name
        self.address = address
        self.website = website
        self.phone_number = phone_number
        self.rating = rating
        self.reviews = reviews
        self.image = image
        self.pricing = pricing
        self.category = category
        self.timing = timing
        self.description = description
        self.servicing = servicing


class Searching:
    def __init__(self, search_key, pages):
        self.search_key = search_key
        self.pages = pages
        self.result = self.start_searching()

    def get_title(self, driver):
        title = 'N/A'
        try:
            title = driver.find_element(
                By.CSS_SELECTOR, 'h2[data-attrid="title"]').text

        except:
            print('title_error')
        return title.replace(',', ' ')

    def get_address(self, driver):
        address = 'N/A'
        try:
            temp_obj = driver.find_element(
                By.XPATH, '//span[@class = "LrzXr"]')
            address = temp_obj.text
        except NoSuchElementException:
            print('address_error')
        return address.replace(',', ' ')

    def get_website(self, driver):
        website = 'N/A'
        try:
            temp_obj = driver.find_element(By.XPATH, '//a[@class="dHS6jb"]')
            website = temp_obj.get_attribute('href')
        except NoSuchElementException:
            print('website_error')
        return website.replace(',', ' ')

    def get_phone_number(self, driver):
        phone = 'N/A'
        try:
            temp_obj = driver.find_element(
                By.CSS_SELECTOR, 'div[data-attrid="kc:/collection/knowledge_panels/has_phone:phone"] span:nth-child(2) > span > a > span')
            phone = temp_obj.text

        except NoSuchElementException:
            print('phone_number_error')
        return phone

    def get_rating(self, driver):
        rating = '-1'
        try:
            temp_obj = driver.find_element(
                By.CSS_SELECTOR, 'g-review-stars span')
            rating = temp_obj.get_attribute('aria-label').replace('，', '')
            start_loc = rating.find('：')
            end_loc = rating.find(' (')
            rating = rating[start_loc + 1:end_loc]

        except NoSuchElementException:
            print('rating_error')
        return rating

    def get_reviews(self, driver):
        reviews = []

        more_btn = driver.find_element(
            By.XPATH, '//g-more-link[@class="mIKy0c OSrXXb tiS4rf"]/span[2]')
        more_btn.click()
        driver.implicitly_wait(2)
        pane = driver.find_element(
               By.XPATH, '//div[@jscontroller="nXizP"]')  # 滑到視窗最下面
        for i in range(3):
                # driver.execute_script("arguments[0].send_keys(Keys.END)", pane)
                pane.send_keys(Keys.END)
                time.sleep(5)

        comments = driver.find_elements(
                By.XPATH, '//div[@class="Jtu6Td"]/span/span')
        for comment in comments:
            print(comment.text)

        return reviews

    def get_image(self, driver):
        image = 'N/A'
        try:
            temp_obj = driver.find_element(
                By.CSS_SELECTOR, 'div[data-attrid="kc:/location/location:media"] > div > a > div')
            if len(temp_obj.get_attribute('style')) > 0:
                image = temp_obj.get_attribute('style')
                if 'background' in image:
                    image = image.replace('background-image: url("', '')
                    image = image.replace('"', '')
                    image = image.replace(');', '')

            else:
                print('image_error')
        except NoSuchElementException:
            print('image_error')
        return image

    def get_category_and_pricing(self, driver):
        category, pricing = 'N/A', '-1'
        try:
            temp_obj = driver.find_elements(
                By.XPATH, '//span[@class="YhemCb"]')
            if len(temp_obj) == 2:
                pricing = temp_obj[0].text.count('$')
                category = temp_obj[1].text

            elif len(temp_obj) == 1:
                category = temp_obj[0].text.replace(',', ' ')

        except NoSuchElementException:
            print('category_error')
        return pricing, category

    def get_timing(self, driver):
        timing_dic = {'星期一': 'N/A', '星期二': 'N/A', '星期三': 'N/A', '星期四': 'N/A', '星期五': 'N/A',
                      '星期六': 'N/A', '星期日': 'N/A'}
        try:
            temp_obj = driver.find_elements(
                By.XPATH, '//table[@class="WgFkxc"]/tbody/tr/td')
            try:
                for i in range(0, 13, 2):
                    timing_dic[temp_obj[i].get_attribute(
                        "innerText")] = temp_obj[i+1].get_attribute("innerText").replace(',', ' ')
            except IndexError:
                print('timing_error')
        except NoSuchElementException:
            print('timing_error')
        return timing_dic

    def get_description(self, driver):
        description = 'N/A'
        try:
            temp_obj = driver.find_element(By.XPATH, '//span[@class="Yy0acb"]')
            description = temp_obj.text
        except NoSuchElementException:
            print('description_error')
        return description.replace(',', ' ')

    def get_servicing(self, driver):
        servicing = 'N/A'
        try:
            temp_obj = driver.find_element(
                By.XPATH, '//div[@class="wDYxhc NFQFxe viOShc"]/c-wiz[1]/div[1]')
            servicing = temp_obj.text
            start_loc = servicing.find(':')
            servicing = servicing[start_loc + 1:].replace(' ', '')

        except NoSuchElementException:
            print('servicing_error')
        return servicing

    def start_searching(self):
        options = webdriver.ChromeOptions()
        s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.page_load_strategy = 'eager'
        #options.headless = True
        driver = webdriver.Chrome(service=s, options=options)
        driver.get('https://www.google.com')
        driver.implicitly_wait(2)

        driver.find_element(By.NAME, "q").send_keys(
            self.search_key + Keys.ENTER)
        more = driver.find_element(By.TAG_NAME, "g-more-link")
        more_btn = more.find_element(By.TAG_NAME, "a")
        more_btn.click()
        time.sleep(5)

        restaurant_list = []
        for page in range(2, self.pages + 1):
            elements = driver.find_elements(
                By.CSS_SELECTOR, 'div#search a[class="vwVdIc wzN8Ac rllt__link a-no-hover-decoration"')
            counter = 1
            for element in elements:
                data_cid = element.get_attribute('data-cid')
                element.click()
                time.sleep(5)

                name = self.get_title(driver)
                print(f'{counter}. now processing... {name}')
                address = self.get_address(driver)
                website = self.get_website(driver)
                phone_number = self.get_phone_number(driver)
                rating = self.get_rating(driver)
                image = self.get_image(driver)
                pricing, category = self.get_category_and_pricing(driver)
                timing = self.get_timing(driver)
                description = self.get_description(driver)
                servicing = self.get_servicing(driver)
                reviews = self.get_reviews(driver)

                restaurant_list.append(Restaurant(name, address, website, phone_number, rating,
                                                  reviews, image, pricing, category, timing, description, servicing))
                counter += 1
            try:
                page_button = driver.find_element(
                    By.CSS_SELECTOR, 'a[aria-label="Page ' + str(page) + '"]')
                page_button.click()
                print('page click... 10 seconds...')
                time.sleep(10)
            except NoSuchElementException:
                break
        driver.quit()
        return restaurant_list


class Storing:
    def __init__(self, searching_obj: Searching):
        self.filename = searching_obj.search_key
        self.raw_data = searching_obj.result
        self.filename_for_mysql = searching_obj.search_key.replace(" ", "_")

    def storing_mysql(self):
        database = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="12345678",
            database="google_map",
            port=3306)

        cursor = database.cursor()
        cursor.execute(f"CREATE TABLE  IF NOT EXISTS {self.filename_for_mysql} (name VARCHAR(50), address TEXT, \
                        website TEXT, phone_number TEXT, rating FLOAT, review1 TEXT, \
                        review2 TEXT, review3 TEXT, image TEXT, pricing INTEGER, \
                        category TEXT, timing_mon TEXT, timing_tue TEXT, timing_wed TEXT, \
                        timing_thu TEXT, timing_fri TEXT, timing_sat TEXT, timing_sun TEXT, \
                        description TEXT, servicing TEXT);")

        for restaurant in self.raw_data:
            command = f"INSERT INTO {self.filename_for_mysql}(name, address, "\
                f"website, phone_number, rating, review1, "\
                f"review2, review3, image, pricing, "\
                f"category, timing_mon, timing_tue, timing_wed, "\
                f"timing_thu, timing_fri, timing_sat, timing_sun, "\
                f"description, servicing) VALUES ('{restaurant.name}', "\
                        f"'{restaurant.address}', '{restaurant.website}', '{restaurant.phone_number}', "\
                        f"{restaurant.rating}, '{restaurant.reviews[0]}', "\
                        f"'{restaurant.reviews[1]}', '{restaurant.reviews[2]}', "\
                        f"'{restaurant.image}', {restaurant.pricing}, '{restaurant.category}', "\
                        f"'{restaurant.timing['星期一']}', '{restaurant.timing['星期二']}', "\
                        f"'{restaurant.timing['星期三']}', '{restaurant.timing['星期四']}', "\
                        f"'{restaurant.timing['星期五']}', '{restaurant.timing['星期六']}', "\
                        f"'{restaurant.timing['星期日']}', '{restaurant.description}', "\
                        f"'{restaurant.servicing}');"
            cursor.execute(command)

        database.commit()
        cursor.close()
        database.close()

    def storing_csv(self):
        if not (os.path.exists(f'{self.filename}.csv')):
            with open(f'{self.filename}.csv', 'w', encoding='utf-8', newline='') as data_csv:
                writer = csv.writer(data_csv)
                info_row = ['name', 'address', 'website', 'phone_number', 'rating',
                            'reviews1', 'reviews2', 'reviews3', 'image', 'pricing', 'category', 'timing1', 'timing2', 'timing3', 'timing4', 'timing5', 'timing6', 'timing7', 'description', 'servicing']
                writer.writerow(info_row)
                for restaurant in self.raw_data:
                    data_row = [restaurant.name, restaurant.address, restaurant.website, restaurant.phone_number,
                                restaurant.rating, restaurant.reviews[0], restaurant.reviews[1], restaurant.reviews[2],
                                restaurant.image, restaurant.pricing, restaurant.category,
                                restaurant.timing['星期一'], restaurant.timing['星期二'],
                                restaurant.timing['星期三'], restaurant.timing['星期四'], restaurant.timing['星期五'],
                                restaurant.timing['星期六'], restaurant.timing['星期日'], restaurant.description] + restaurant.servicing
                    writer.writerow(data_row)
                data_csv.close()


def multithreading(target_func, processing_data):  # 用在掃瞄data的時候
    threads = []  # 多執行緒
    threads_num = 5
    while len(processing_data) > 0:
        if len(processing_data) < threads_num:
            t = len(processing_data)
        else:
            t = threads_num
        for i in range(t):
            threads.append(threading.Thread(
                target=target_func, args=(processing_data[i],)))
        for i in range(t):
            threads[i].start()
        for i in range(t):
            threads[i].join()

        processing_data = processing_data[t:]
        threads = []


def processing(info):
    m = Searching(f"Taipei {info[0]} {info[1]}", info[2])
    n = Storing(m)
    n.storing_mysql()


def main():
    print('Please type in your location: ', end='')
    loc = str(input())
    print('Please type in your searching items (must be seperated with only ","): ', end='')
    items = str(input()).split(',')
    print('Please type in the pages you want to search (2 by default)： ', end='')
    pages = int(input())
    info = [(loc, item, pages) for item in items]
    # l = ['steak', 'pasta', 'ramen', 'cafe', 'noodles', 'sushi', 'drinks', 'bakery', 'hamburger', 'breakfast', 'hotpot']
    # multithreading(processing, info)

'''
if __name__ == "__main__":
    main()
'''


m = Searching("Taipei gongguan steak", 2)
