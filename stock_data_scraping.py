from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import select
from selenium.webdriver.chrome.service import Service
import time
import datetime
import csv
import random
import os
import re
import threading
import copy
from os import listdir

class stock:
        def __init__(self, name, num, category, capital_amount, share_capital=0):
                self.name = name
                self.num = num
                self.category = category
                self.capital_amount = capital_amount
                self.share_capital = share_capital
                self.datas = []

class ip_searcher:
        def free_proxy_list_net(self):  # from https://free-proxy-list.net/
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--headless")     
                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                driver = webdriver.Chrome(service = s, options=chrome_options)
                driver.get("https://www.sslproxies.org/")
                _ = driver.find_element(By.XPATH, "/html[1]/body[1]/section[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]")
                proxy_ips = re.findall('\d+\.\d+\.\d+\.\d+ \d+', _.text)
                driver.quit()
                return proxy_ips

        def geonode_com(self):  # from https://geonode.com/free-proxy-list/
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--headless")     
                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                driver = webdriver.Chrome(service = s, options=chrome_options)
                driver.get("https://geonode.com/free-proxy-list/")
                driver.find_element(By.XPATH, \
                                        '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/label[1]').click()
                driver.find_element(By.XPATH, \
                                        '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/label[2]').click()
                time.sleep(1)
                driver.find_element(By.XPATH, \
                                        '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]/label[1]').click()
                driver.find_element(By.XPATH, \
                                        '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]/label[2]').click()
                driver.execute_script("window.scrollTo(0,400)")
                '''
                __ = driver.find_element(By.CSS_SELECTOR, \
                                        '#fast')
                driver.execute_script("arguments[0].click();", __)

                '''
                time.sleep(6)
                _ = driver.find_element(By.XPATH, '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[4]/table[1]/tbody[1]')
                
                proxy_ips = re.findall('\d+\.\d+\.\d+\.\d+ \d+', _.text)
                driver.quit()
                return proxy_ips

class data_initializer:
        
        def __init__(self, start_time, end_time, using_proxy):
                self.start_time = list(map(lambda x: int(x), start_time.split('/')))
                self.end_time = list(map(lambda x: int(x), end_time.split('/')))
                #  格式採1/2這種
                self.base_rows = ['公司名', '股號', '類別', '資本額', '流通在外股數']  # 六個字以內
                
                self.month_list = self.generate_list_of_months(self.start_time[0], self.start_time[1]\
                                                        , self.end_time[0], self.end_time[1]) \

                self.season_list = self.generate_list_of_seasons()
                self.date_list = self.generate_list_of_dates()
                
                self.using_proxy = using_proxy
                self.valid_ips = self.generate_ips()
                
                self.stock_list = self.upgrade_stock_list()
                self.stock_num_list = [x.num for x in self.stock_list]

                self.filenames_refer = {'stock_bal_sheet': '_bal', 'stock_income_statement': '_inc', \
                                        'stock_sales_revenue': '_rev', 'stock_info': '', 'stock_sc_trading': '_sc_trading', \
                                        'stock_trading': '_trading', 'stock_basic': '_base', 'stock_technic': '_technic'}

                self.no_data = self.generate_no_data()
                
                self.options = webdriver.ChromeOptions()
                self.options.page_load_strategy = 'eager'
                self.options.add_argument('--disable-dev-shm-usage')
                self.options.add_argument('--disable-gpu')
                self.options.add_argument("blink-settings=imagesEnabled=false")
                self.options.add_argument("--headless")
                self.options.add_argument('--log-level=3')

        def change_data_zone(self, start_time, end_time):
                self.start_time = list(map(lambda x: int(x), start_time.split('/')))
                self.end_time = list(map(lambda x: int(x), end_time.split('/')))
                #  格式採1/2這種
                self.month_list = self.generate_list_of_months(self.start_time[0], self.start_time[1]\
                                                                            , self.end_time[0], self.end_time[1])              
        def generate_ips(self):
                valid_ips = []
                if self.using_proxy:
                        searcher = ip_searcher()
                        proxy_ips = searcher.free_proxy_list_net()
                        s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                        for i in range(len(proxy_ips)):
                                if len(valid_ips) >= 20:  # ip 最大數量為20
                                        break
                                __ = proxy_ips[i].split(' ')
                                chrome_options = webdriver.ChromeOptions()
                                chrome_options.add_argument("--headless")
                                chrome_options.add_argument('--proxy-server='+'http://'+__[0]+':'+__[1])
                                driver = webdriver.Chrome(service=s, options=chrome_options)
                                try:
                                        driver.set_page_load_timeout(5)
                                        driver.get('http://httpbin.org/ip')
                                        valid_ips.append(__[0] + ':' + __[1])
                                except:
                                        pass
                                driver.close()
                return valid_ips

        def generate_sc_values(self):
                if not(os.path.exists(f'D:/sc_values.csv')):
                        url = "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?"
                        ip = self.headers_set()
                        s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                        driver = webdriver.Chrome(service = s, options = self.options)
                        driver.get(url)

                        sc_options = driver.find_elements(By.CSS_SELECTOR,\
                                          "td.t0 table.t01 tbody:nth-child(2) tr:nth-child(1) td.t10 select:nth-child(2) > option")
                        sc_values = list(map(lambda x: x.get_attribute("value"), sc_options))
                        result = []
                        for x in sc_values:
                                driver.get(url + f'a={x}&b={x}')
                                time.sleep(1)
                                loc_options = driver.find_elements(By.CSS_SELECTOR,\
                                                  "td.t0 table.t01 tbody:nth-child(2) tr:nth-child(1) td.t10 select:nth-child(3) > option")
                                result.append(list(map(lambda y: y.get_attribute("value"), loc_options)))

                        driver.quit()
                        with open('D:/sc_values.csv', 'w', newline='') as stock_csv:
                                writer = csv.writer(stock_csv)
                                writer.writerows(result)
                                stock_csv.close()
        def generate_no_data(self):
                result = []
                filename = 'D:/stock_no_data.csv'
                if os.path.exists(filename):
                        with open(filename, 'r') as stock_csv:
                                reader = csv.reader(stock_csv)
                                list_of_rows = list(reader)
                                stock_csv.close()
                        os.remove('D:/stock_no_data.csv')
                        for x in list_of_rows:
                                if x not in result:
                                        result.append(x)
                        with open(filename, 'w', newline = '') as new_csv:
                                writer = csv.writer(new_csv)
                                writer.writerows(result)
                                new_csv.close()

                return result
                
        def update_weighted_stock(self):  # 爬權值股資訊，每個月更新一次
                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                driver = webdriver.Chrome(service = s, options = self.object.options)
                driver.get("https://www.taifex.com.tw/cht/9/futuresQADetail")

                _ = driver.find_element(By.XPATH, ('//tbody'))
                _ = _.text.split("\n")[6:]
                list_of_rows = []
                for x in _:
                        __ = x.split(' ')
                        list_of_rows.append(__[:4])
                        list_of_rows.append(__[4:])
                if len(list_of_rows[-1]) == 0:
                        list_of_rows = list_of_rows[:-1]
                driver.quit()
                list_of_rows = sorted(list_of_rows, key=lambda x: int(x[0]))
                with open('D:/stock_info/' + 'weighted_stock.csv', 'w', newline = '') as stock_csv:
                        writer = csv.writer(stock_csv)
                        writer.writerows(list_of_rows)
                        stock_csv.close()


        def generate_list_of_dates(self):
                files = listdir('D:/stock_info/')
                if len(files) == 0:
                        return -1
                samples = random.choices(files, k=10)
                refer = []
                refer_set = []
                for sample in samples:
                        with open('D:/stock_info/' + sample, 'r') as stock_csv:
                                
                                reader = csv.reader(stock_csv)
                                list_of_rows = list(reader)
                                if len(list_of_rows) != 0:
                                        result = [x[0] for x in list_of_rows]
                                else:
                                        result = []
                                stock_csv.close()
                        refer.append(result)
                
                for x in refer:
                        if x not in refer_set:
                                refer_set.append((x, refer.count(x)))
                result = sorted(refer_set, key=lambda x:x[1], reverse=True)
                return result[0][0]
        
        def generate_list_of_months(self, start_year, start_month, end_year, end_month):
                _ = end_year - start_year + 1
                if _ == 1:
                        months_list = [x for x in range(start_month, end_month + 1)]
                else:
                        months_list = [x for x in range(start_month, 13)] + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]*(_-2) \
                                           + [x for x in range(1, end_month + 1)]
                years_list = []
                __ = start_year
                for i in range(len(months_list)):
                        if months_list[i] == 1 and i != 0:
                                __ += 1
                        years_list.append(__)

                return list(zip(years_list, months_list))

        def generate_list_of_seasons(self):
                ref = {1:1, 2:1, 3:1, 4:2, 5:2, 6:2, 7:3, 8:3, 9:3, 10:4, 11:4, 12:4}
                result = []
                result_y = []
                for x in self.month_list:
                        if ref[x[1]] not in result:
                                result.append(ref[x[1]])
                                result_y.append(x[0])
                return list(zip(result_y, result))

        def headers_set(self):
                if self.using_proxy is True:
                        if self.valid_ips == []: 
                                self.valid_ips = self.generate_ips()
                        __ = random.choice(self.valid_ips)
                        webdriver.DesiredCapabilities.CHROME['proxy'] = {
                                "httpProxy": __,
                                "ftpProxy": __,
                                "sslProxy": __,
                                "proxyType": "MANUAL",

                        }
                        webdriver.DesiredCapabilities.CHROME['acceptSs;Certs'] = True
                user_agent_list = [ \
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",\
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",\
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36", \
                        "Mozilla/5.0 (Linux; Android 10; SM-G996U Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36", \
                        "Mozilla/5.0 (Linux; Android 11; Pixel 5 Build/RQ3A.210805.001.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile Safari/537.36"]
                _ = random.choice(user_agent_list)
                self.options.add_argument(f"User-Agent={_}")

                if self.using_proxy is True:
                        return __
                else:
                        return -1

        def upgrade_stock_list(self):
                stock_list = []
                with open('C:/Users/profe/Downloads/t187ap03_L.csv', 'r', encoding='utf-8') as csv_file:
                        csv_reader = csv.reader(csv_file)
                        list_of_rows = list(csv_reader)
                        _ = len(list_of_rows)
                        for i in range(1, _):
                                __ = stock(list_of_rows[i][3], list_of_rows[i][1], int(list_of_rows[i][5]), \
                                           float(list_of_rows[i][17]))
                                stock_list.append(__)
                        csv_file.close()
                return stock_list
                 
        def find_monthly_data_of_price(self, target_year, target_month, target_stock_num):  # 價量, 以int西元、int月份
                while True:
                        try:
                                ip = self.headers_set()

                                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                                driver = webdriver.Chrome(service = s, options = self.options)
                                driver.get(\
                                        f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=html&date={target_year}{target_month:02d}01&stockNo={target_stock_num}")
                                time.sleep(random.randint(5, 10))

                                info_rows = driver.find_elements(By.XPATH, "//tbody/tr/td")
                                columns = 9
                                datas = []
                                for i in range(len(info_rows)//columns):
                                        _ = []
                                        for j in range(columns):
                                                try:
                                                        __ = info_rows[0].text
                                                        __ = float(__.replace(',', ''))
                                                        _.append(__)
                                                except:
                                                        _.append(info_rows[0].text)
                                                info_rows.pop(0)
                                        datas.append(_)
                                time.sleep(1)
                                driver.close()
                                return datas
                        except:
                                print(self.valid_ips)
                                if self.using_proxy is True:
                                        self.valid_ips.remove(ip)
                                if self.valid_ips == []:
                                        break
                                driver.close()
                                time.sleep(1)
                                
        def check_fin_data(self, target_stock_num, type_of_statement):
                if type_of_statement == "bal":
                        file_name = 'D:/stock_bal_sheet/' + f"{target_stock_num}_bal.csv"
                        refer = ['時間'] + [f"{x[0]}/{x[1]}" for x in self.season_list]
                        key_loc = 0
                elif type_of_statement == "inc":
                        file_name = 'D:/stock_inc_statement/' + f"{target_stock_num}_inc.csv"
                        refer = ['時間'] + [f"{x[0]}/{x[1]}" for x in self.season_list]
                        key_loc = 0
                elif type_of_statement == 'rev':
                        file_name = 'D:/stock_sales_rev/' + f"{target_stock_num}_rev.csv"
                        refer = ['時間'] + [f"{x[0]}/{x[1]}" for x in self.month_list]
                        key_loc = 0
                elif type_of_statement == 'trading':
                        file_name = "D:/stock_trading/" + f"{target_stock_num}_trading.csv"
                        refer = ['時間'] + self.date_list
                        key_loc = 0
                elif type_of_statement == 'sc_trading':
                        file_name = "D:/stock_sc_trading/" + f"{target_stock_num}_sc_trading.csv"
                        refer = ['時間'] + self.date_list
                        key_loc = 0
                elif type_of_statement == 'stock_basic':
                        file_name = "D:/stock_basic/" + f"{target_stock_num}_basic.csv"
                        refer = self.base_rows
                        key_loc = 0

                result = {}
                if os.path.exists(file_name):
                        with open(file_name, 'r') as stock_csv:
                                reader = csv.reader(stock_csv)
                                list_of_rows = list(reader)
                                for x in list_of_rows:
                                        _ = x[key_loc]  # 110/1
                                        if _ not in result:
                                                result[_] = []
                                        if _ in refer and x not in result[_]:
                                                result[_] = x
                                                
                                stock_csv.close()
                                os.remove(file_name)  # 刪掉舊檔案
                return result, file_name, refer

        def check_stock_data(self, target_stock_num):
                result = {x: [] for x in self.month_list}
                file_name = f'D:/stock_info/{target_stock_num}.csv'
                if os.path.exists(file_name):
                        with open(file_name, 'r') as stock_csv:
                                reader = csv.reader(stock_csv)
                                list_of_rows = list(reader)
                                for x in list_of_rows:
                                        month_str = (int(x[0][:3]), int(x[0][4:6]))
                                        if month_str in self.month_list and x not in result[month_str]:
                                                result[month_str].append(x)
                                stock_csv.close()
                                os.remove(file_name)  # 刪掉舊檔案
                return result, file_name

        def find_basic_info(self, target_stock):
                print(f' -- {target_stock.num} processing...')
                result = self.check_fin_data(target_stock.num, 'stock_basic')
                old_data = result[0]
                filename = result[1]
                refer = result[2]
                with open(filename, 'w', newline = '') as stock_csv:
                        writer = csv.writer(stock_csv)
                        _ = [target_stock.name, target_stock.num, target_stock.category, target_stock.capital_amount]
                        if refer[4] not in old_data:
                                _.append(self.find_share_capital(target_stock.num))
                        rows = [[refer[i], _[i]] if refer[i] not in old_data \
                                else old_data[refer[i]] for i in range(len(refer))]
                        writer.writerows(rows)
                        stock_csv.close()
                
        def find_fin_data(self, target_year, target_season, type_of_statement):  # 皆以數字，bal、inc
                if type_of_statement == "bal":
                        url = "https://mops.twse.com.tw/mops/web/t163sb05"
                elif type_of_statement == "inc":
                        url = "https://mops.twse.com.tw/mops/web/t163sb04"
                
                ip = self.headers_set()
                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                driver = webdriver.Chrome(service = s, options = self.options)
                driver.get(url)
                time.sleep(random.randint(1, 3))

                market = driver.find_element(By.XPATH, '//select[@id="TYPEK"]')
                market_select = select.Select(market)
                market_select.select_by_value("sii")
                time.sleep(random.randint(1, 3))

                year = driver.find_element(By.XPATH, '//input[@id="year"]')
                year.send_keys(str(target_year))
                time.sleep(random.randint(1, 3))

                season = driver.find_element(By.XPATH, "//select[@id='season']")
                season_select = select.Select(season)
                season_select.select_by_visible_text(str(target_season))
                time.sleep(random.randint(1, 3))

                refer_button = driver.find_element(By.XPATH, '//tbody/tr[1]/td[2]/div[1]/div[1]/input[1]')
                refer_button.click()
                time.sleep(random.randint(5, 10))

                tables = driver.find_elements(By.XPATH, '//body[1]/center[1]/table[1]/tbody[1]/tr[1]/td[1]/div[4]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/table[1]/tbody[1]/tr[1]/td[3]/div[1]/div[5]/div[1]/table')
                for x in tables:
                        table = x.text.split('\n')[1:]
                        rows = [y.split(' ') for y in table]
                        for i in range(1, len(rows)):
                                stock_num = rows[i][0]
                                result = self.check_fin_data(stock_num, type_of_statement)
                                old_data = result[0]
                                file_name = result[1]
                                seasons = result[2]
                                with open(file_name, 'w', newline = '') as stock_csv:
                                        writer = csv.writer(stock_csv)
                                        for y in seasons:
                                                if y in old_data:
                                                        writer.writerow(old_data[y])
                                                elif y == seasons[0]:
                                                        writer.writerow([seasons[0]] + rows[0][2:])
                                                elif y == f"{target_year}/{target_season}":
                                                        writer.writerow([y] + rows[i][2:])
                                                        
                                        stock_csv.close()
                driver.close()

        def find_share_capital(self, target_stock_num):
                while True:
                        ip = self.headers_set()
                        try:  # 防止定位不到元素的error
                                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                                driver = webdriver.Chrome(service = s, options = self.options)
                                driver.get("https://mops.twse.com.tw/mops/web/t05st03")
                                time.sleep(random.randint(1, 3))

                                stock_input = driver.find_element(By.XPATH, "//input[@id='co_id']")
                                stock_select = stock_input.send_keys(target_stock_num)
                                time.sleep(random.randint(1, 3))

                                refer_button = driver.find_element(By.XPATH, "//tbody/tr[1]/td[2]/div[1]/div[1]/input[1]")
                                refer_button.click()
                                time.sleep(random.randint(1, 3))
                  
                                target_data = driver.find_element(By.XPATH, "/html[1]/body[1]/center[1]/table[1]/tbody[1]/tr[1]/td[1]/div[4]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/table[1]/tbody[1]/tr[1]/td[3]/div[1]/div[5]/div[1]/table[2]/tbody[1]/tr[12]/td[1]")
                                share_capital = target_data.text
                                time.sleep(random.randint(1, 3))
                                return share_capital
                        except:
                                if self.valid_ips == []:
                                        break
                                if self.using_proxy is True:
                                        self.valid_ips.remove(ip)
                                time.sleep(1)
                        driver.quit()
                        
        def store_stock_data(self, target_stock):
                result = self.check_stock_data(target_stock.num)
                old_data = result[0]
                filename = result[1]
                with open(filename, 'a', newline = '') as stock_csv:
                        writer = csv.writer(stock_csv)
                        for x in self.month_list:
                                if len(old_data[x]) != 0:  # 在前份檔案有資料的狀況
                                        writer.writerows(old_data[x])
                                elif [target_stock.num, str(x[0]), str(x[1])] not in self.no_data:
                                        __ = self.find_monthly_data_of_price(x[0]+1911, x[1], target_stock.num)
                                        if __ == []:
                                                print([target_stock.num, str(x[0]), str(x[1])])
                                                with open('D:/stock_no_data.csv', 'a', newline = '') as info_csv:
                                                        writer2 = csv.writer(info_csv)
                                                        writer2.writerow((target_stock.num, x[0], x[1]))
                                                        info_csv.close()
                                        else:
                                                writer.writerows(__)
                                        
                        stock_csv.close()
                
        
        def find_sales_revenue(self, target_year, target_month):
                
                url = f"https://mops.twse.com.tw/nas/t21/sii/t21sc03_{target_year}_{target_month}_0.html"
                
                Options = copy.deepcopy(self.options)
                prefs = {'profile.default_content_settings.popups': 0,
                         "download.default_directory":r'C:\Users\profe\Downloads'}
                Options.add_experimental_option("prefs",prefs)
                
                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                driver = webdriver.Chrome(service = s, options=Options)
                driver.get(url)
                time.sleep(random.randint(1, 3))

                button = driver.find_element(By.XPATH, '/html[1]/body[1]/center[1]/center[1]/font[2]/input[1]')
                button.click()
                time.sleep(random.randint(1, 3))
                driver.close()
                
                file = f"t21sc03_{target_year}_{target_month}.csv"
                with open("C:/Users/profe/Downloads/" + file, 'r', encoding='utf-8') as stock_csv:
                        reader = csv.reader(stock_csv)
                        list_of_rows = list(reader)
                        stock_csv.close()
                        os.remove("C:/Users/profe/Downloads/" + file)

                for x in list_of_rows[1:]:
                        stock_num = x[2]
                        result = self.check_fin_data(stock_num, 'rev')
                        old_data = result[0]
                        file_name = result[1]
                        months = result[2]
                        with open(file_name, 'w', newline = '') as stock_csv:
                                writer = csv.writer(stock_csv)
                                for y in months:
                                        if y in old_data:
                                                writer.writerow(old_data[y])
                                        elif y == months[0]:
                                                writer.writerow([months[0]] + list_of_rows[0][5:])
                                        elif y == f"{target_year}/{target_month}":
                                                writer.writerow([y] + x[5:])
                                stock_csv.close()

        def find_stock_trading(self, date_str): # 110/01/01
                print(f" -- {date_str} -- processing...")
                date_l = list(map(lambda x:int(x), date_str.split('/')))
                target_year, target_month, target_day = date_l[0], date_l[1], date_l[2]
                url = f"https://www.twse.com.tw/fund/T86?response=html&date={target_year+1911}{target_month}{target_day}&selectType=ALLBUT0999"
                ip = self.headers_set()                
                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                driver = webdriver.Chrome(service = s, options = self.options)
                driver.get(url)
                time.sleep(0.5)

                _ = driver.find_elements(By.XPATH, '//thead/tr[2]/td')
                __ = driver.find_elements(By.XPATH, '//tbody/tr')
                head = list(map(lambda x: x.text, _))
                table = list(map(lambda x: x.text.split(' '), __))
                driver.quit()
                
                base_data = ['時間'] + head

                for x in table:
                        if x[0] in self.stock_num_list:
                                result = self.check_fin_data(x[0], 'trading')
                                old_data = result[0]
                                file_name = result[1]
                                dates = result[2]
                                with open(file_name, 'w', newline = '') as stock_csv:
                                        writer = csv.writer(stock_csv)                                        
                                        for y in dates:
                                                if y in old_data:
                                                        writer.writerow(old_data[y])
                                                elif y == dates[0]:
                                                        writer.writerow(base_data)
                                                elif y == date_str:
                                                        x_float = list(map(lambda a: float(a.replace(',', '')), x[2:]))
                                                        writer.writerow([y] + x_float)
                                        stock_csv.close()

        def find_stock_sc_trading(self, date_str, share_or_money):  # 張數或金額, share or money
                print(f" -- {date_str} -- processing...")
                
                url = "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=5860&b=5860&c=B&e=2021-9-17&f=2021-9-17"
                date_l = list(map(lambda x:int(x), date_str.split('/')))
                target_year, target_month, target_day = date_l[0], date_l[1], date_l[2]
                ip = self.headers_set()                
                s = Service(r"C:/Users/profe/Desktop/chromedriver.exe")
                driver = webdriver.Chrome(service = s)
                driver.get(url)
                time.sleep(0.5)
                
                '''
                                buy = driver.find_elements(By.CSS_SELECTOR, \
                                                           "td.t0 table.t01 tr:nth-child(3) td:nth-child(1) table.t0 tbody:nth-child(1) > tr")[2:]
                                          
                                sell = driver.find_elements(By.CSS_SELECTOR, \
                                                                 "td.t0 table.t01 tr:nth-child(3) td:nth-child(2) table.t0 tbody:nth-child(1) > tr")[2:]
                                buy_table = sorted([x.text.split(' ') for x in buy])
                                sell_table = sorted([x.text.split(' ') for x in sell])
                                print(buy_table)
                
                                for stock_data_row in buy_table:
                                        stock_num = stock_data_row[0][:4]
                                        result = check_fin_data(stock_num, 'sc_trading')
                                        old_data = result[0]
                                        filename = result[1]
                                        dates = result[2]

                                        with open(filename, 'w', newline = '') as stock_csv:
                                                writer = csv.writer(stock_csv)
                                                
                time.sleep(random.randint(1, 3))
        '''
        def two(self, target_stock):
                self.find_basic_info(target_stock)
                self.store_stock_data(target_stock)
        
        def multithreading(self, target_func, processing_data):  # 用在掃瞄data的時候
                threads = [] # 多執行緒
                threads_num = 5
                while len(processing_data) > 0:
                        if len(processing_data) < threads_num:
                                t = len(processing_data)
                        else:
                                t = threads_num
                        for i in range(t):
                                threads.append(threading.Thread(target=target_func, args = (processing_data[i],)))
                        for i in range(t):
                                threads[i].start()
                        for i in range(t):
                                threads[i].join() 
                        if self.using_proxy and self.valid_ips == []:
                                break
                        processing_data = processing_data[t:]
                        threads = []

class data_analyzer(data_initializer):
        def __init__(self, start_time, end_time, using_proxy):
                data_initializer.__init__(self, start_time, end_time, using_proxy)
                self.data_types = {'3ma': [], '5ma': [], '10ma': [], '20ma':[], '60ma':[], 'k':[], 'd':[]}

        def store_tech_data(self, target_stock_num):
                filename = 'D:/stock_technic/' + f'{target_stock_num}{self.filenames_refer["stock_technic"]}.csv'

                if os.path.exists(filename):
                        os.remove(filename)

                with open('D:/stock_info/' + f"{target_stock_num}.csv", 'r') as stock_csv:
                        reader = csv.reader(stock_csv)
                        list_of_rows = list(reader)
                        stock_csv.close()

                prices = []
                out_of_cal = []
                for x in list_of_rows:
                        if '--' in x:
                                out_of_cal.append(x[0])
                        else:
                                prices.append(x)

                with open(filename, 'w', newline='') as stock_csv:
                        writer = csv.writer(stock_csv)
                        kd = self.calculate_kd(prices)
                        ma3 = self.calculate_ma(prices, 3)
                        ma5 = self.calculate_ma(prices, 5)
                        ma10 = self.calculate_ma(prices, 10)
                        ma20 = self.calculate_ma(prices, 20)
                        ma60 = self.calculate_ma(prices, 60)

                        for i in range(len(list_of_rows)):
                                if list_of_rows[i][0] in out_of_cal:
                                        writer.writerow(['--' * len(self.data_types)])
                                else:
                                        a = (ma3[i], ma5[i])
                                        a2 = (ma10[i], ma20[i], ma60[i])
                                        b = (kd[0][i], kd[1][i])
                                             
                                        writer.writerow((ma3[i], ma5[i], ma10[i], ma20[i], ma60[i], kd[0][i], kd[1][i]))

                        stock_csv.close()

        def calculate_kd(self, list_of_rows):
                if len(list_of_rows) < 8:
                        _ = [50 for i in range(len(list_of_rows))]
                        return _, _
                prices = list_of_rows
                result_k = [50 for i in range(8)]
                result_d = [50 for i in range(8)]
                for i in range(8, len(prices)):
                        all_day_highest = [float(x[4]) for x in prices[i-8:i+1]]
                        all_day_lowest = [float(x[5]) for x in prices[i-8:i+1]]

                        all_day_max = max(all_day_highest)
                        all_day_min = min(all_day_lowest)
                        rsv = ((float(prices[i][6]) - all_day_min)/ (all_day_max - all_day_min))* 100
                        k = (result_k[-1]*2 + rsv) / 3
                        d = (result_d[-1]*2 + k) / 3
                        result_k.append(round(k, 2))
                        result_d.append(round(d, 2))
                return result_k, result_d
        
        def calculate_macd(self, list_of_rows):
                prices = list_of_rows


        def calculate_ma(self, list_of_rows, days):
                if len(list_of_rows) < days:
                        return ['--' for i in range(len(list_of_rows))]
                prices = list_of_rows
                result = ['--' for i in range(days-1)]
                for i in range(days - 1, len(prices)):
                        all_day_price = [float(x[6]) for x in prices[i-days+1: i+1]]
                        result.append(round(sum(all_day_price)/days, 2))
                return result    
                
a = data_analyzer('110/4', '111/8', False)
for x in a.date_list:
        a.find_stock_trading(x)

