import csv
import os
import re
import copy
import math
import random
import numpy as np

class data_filter:
        def __init__(self, start_time, end_time, needed_info):
                self.start_time = list(map(lambda x: int(x), start_time.split('/')))
                self.end_time = list(map(lambda x: int(x), end_time.split('/')))
                self.month_list = self.generate_list_of_months(self.start_time[0], self.start_time[1]\
                                                        , self.end_time[0], self.end_time[1])
                self.season_list = self.generate_list_of_seasons()
                self.date_list = self.generate_list_of_dates()
                self.stock_num_list = [f.replace('.csv', '') for f in os.listdir('D:/stock_info/')]

                self.filenames_refer = {'stock_bal_sheet': '_bal', 'stock_income_statement': '_inc', \
                                        'stock_sales_revenue': '_rev', 'stock_info': '', 'stock_sc_trading': '_sc_trading', \
                                        'stock_trading': '_trading', 'stock_basic': '_base'}  
                self.info_dic = self.upgrade_needed_info(needed_info)
                self.parameter_refer = []

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
           
        def generate_list_of_dates(self):
                files = os.listdir('D:/stock_info/')
                samples = random.choices(files, k=10)
                refer = []
                refer_set = []
                for sample in samples:
                        with open('D:/stock_info/' + sample, 'r') as stock_csv:
                                
                                reader = csv.reader(stock_csv)
                                list_of_rows = list(reader)
                                if len(list_of_rows) != 0:
                                        result = [x[0] for x in list_of_rows if (int(x[0][:3]), int(x[0][4:6])) in self.month_list]
                                else:
                                        result = []
                                stock_csv.close()
                        refer.append(result)
                
                for x in refer:
                        if x not in refer_set:
                                refer_set.append((x, refer.count(x)))
                result = sorted(refer_set, key=lambda x:x[1], reverse=True)[0][0]

                return result

        def generate_list_of_seasons(self):
                ref = {1:1, 2:1, 3:1, 4:2, 5:2, 6:2, 7:3, 8:3, 9:3, 10:4, 11:4, 12:4}
                result = []
                result_y = []
                for x in self.month_list:
                        if ref[x[1]] not in result:
                                result.append(ref[x[1]])
                                result_y.append(x[0])
                additional = [(result_y[0], result[0] - 1) if result[0] != 1 else \
                                   (result_y[0] - 1, 12)]  #多留一個月
                return additional + list(zip(result_y, result))

        def upgrade_needed_info(self, needed_info):
                # 採['stock_bal_sheet', 'stock_info', 'stock_trading', 'weighted_stock.csv']形式
                result_by_info = {}  # 先查資料、股號、日期or bases
                for info in needed_info:
                        if info in self.filenames_refer:  # 在資料夾裡的資訊類型
                                result_by_stock = {}
                                for stock in self.stock_num_list:
                                        result_by_dates_or_bases = {}
                                        stock_file = f'D:/{info}/' + f"{stock}{self.filenames_refer[info]}.csv"
                                        if os.path.exists(stock_file):
                                                with open(stock_file, 'r') as stock_csv:
                                                        reader = csv.reader(stock_csv)
                                                        list_of_rows = list(reader)
                                                        for dates_or_bases in list_of_rows:
                                                                try:
                                                                        _ = self.optimizing_numbers(info, dates_or_bases)
                                                                except:
                                                                        print(stock_file)
                                                                if _ != []:
                                                                        result_by_dates_or_bases[dates_or_bases[0]] = _
                                                        stock_csv.close()
                                        result_by_stock[stock] = result_by_dates_or_bases
                        else:
                                with open(f'D:/{info}', 'r') as data_csv:
                                        reader = csv.reader(data_csv)
                                        list_of_rows = list(reader)
                                        result_by_stock = list_of_rows
                                        data_csv.close()
                               
                        result_by_info[info] = result_by_stock
                return result_by_info

        def optimizing_numbers(self, info_type, dates_or_bases):
                if info_type == 'stock_info':
                        if '--' in dates_or_bases:
                                return []
                        if 'X0.00' in dates_or_bases:
                                return [float(x) for x in dates_or_bases[1:7]] + ['X0.00', float(dates_or_bases[-1])]
                        return list(map(lambda x: float(x), dates_or_bases[1:]))
                elif info_type == 'stock_bal_sheet' or info_type == 'stock_income_statement':
                        if dates_or_bases[0] == '時間':
                                return dates_or_bases[1:]
                        result = [x if x == '--' else float(x.replace(',', '')) for x in dates_or_bases[1:]]
                        return result
                return dates_or_bases[1:]


        def find_update_info(self, date_str, type_of_statement, stock_num):
                if type_of_statement == 'bal' or type_of_statement == 'inc':
                        insurance_com = {'2816', '2832', '2850', '2851', '2852'}
                        billfin_com = {'2820'}
                        securities_com = {'2855','6005','6015','6016','6020','6021','6023','6024'}
                        banking_com = {'2801','2809','2812','2834','2836','2838','2845','2849','2897','5880'}
                        fin_com = {'2880','2881','2882','2883','2884','2885','2886','2887','2888','2889','2890','2891','2892','5820'}

                        _ = date_str[4:]
                        if stock_num in insurance_com:
                                refer = sorted(['04/30', '08/31', '10/31', '03/31', _])
                        elif stock_num in billfin_com | securities_com | banking_com | fin_com:
                                refer = sorted(['05/15', '08/31', '11/14', '03/31', _])
                        else:
                                refer = sorted(['05/05', '08/14', '11/14', '03/31', _])
                      
                        if refer[0] == _ or refer[-1] == _:
                                result = f'{int(date_str[:3]) - 1}/3'
                        elif refer[1] == _:
                                result = f'{int(date_str[:3]) - 1}/4'
                        elif refer[2] == _:
                                result = f'{int(date_str[:3])}/1'
                        elif refer[3] == _:
                                result = f'{int(date_str[:3])}/2'

                        if result not in self.season_list:
                                return 'No data'
                        else:
                                return result                                

                elif type_of_statement == 'rev':
                        _ = date_str.split('/')
                        y, m, d = _[0], _[1], _[2]
                        
                        if date_str < f"{y}/{m}/10":
                                if m == '01' or m == '02': 
                                        result = f"{int(y) - 1}/{int(m) + 10}"
                                else:
                                        if m == '12':
                                                result = f"{y}/{int(m) - 2}"
                                        else:
                                                result = f"{y}/0{int(m) - 2}"
                        else:
                                if m == '01':
                                        result = f"{int(y) - 1}/{int(m) + 11}"
                                else:
                                        if m == '11' or m == '12':
                                                result = f"{y}/{int(m) - 1}"
                                        else:
                                                result = f"{y}/0{int(m) - 1}"
                        __ = result.split('/')
                        if (int(__[0]), int(__[1])) not in self.month_list:
                                return 'No data'
                        else:
                                return result
                elif type_of_statement == 'trading':
                        loc = self.date_list.index(date_str)
                        if loc == 0:
                                return 'No data'
                        else:
                                return self.date_list[loc - 1]

class b_trading_amount_method(data_filter):  # 刪除條件：50% 以上天數在榜上、為權值股、為金融股、買紅不買黑
        def __init__(self, starttime, endtime, needed_info, rank_num, higher_then_percent, frequent_ratio):
                self.rank_num = rank_num
                self.higher_then_percent = higher_then_percent
                self.frequent_ratio = frequent_ratio
                data_filter.__init__(self, starttime, endtime, needed_info)
                self.trading_amount_dic = self.upgrade_trading_amount()

        def upgrade_trading_amount(self):  # 日期為key的dic，rank_num預設30
                result = {}
                refer = copy.deepcopy(self.info_dic)
                for x in self.date_list:
                        _ = []
                        for y in self.stock_num_list:
                                try:
                                         data = refer['stock_info'][y][x]
                                         _.append((y, float(data[1])))
                                except KeyError:  # 該股票在該日期沒有資料
                                        pass

                        __ = sorted(_, key= lambda x: x[1], reverse=True)
                        result[x] = __[:self.rank_num]
                return result

        def is_in_trading_amount(self, target_date, target_stock_num):
                nums_on_rank = [x[0] for x in self.trading_amount_dic[target_date]]
                if target_stock_num in nums_on_rank:
                        return True
                return False

        def isnt_weighted(self, target_stock_num):
                weighted_info = self.info_dic['weighted_stock.csv']
                is_weighted = []
                for x in weighted_info:
                        try:
                                if float(x[-1][:-1]) >= self.higher_then_percent:
                                         is_weighted.append(x[1])
                        except:
                                print(x)
                        #is_weighted = [stocks[1] for stocks in weighted_info )]
                
                if target_stock_num not in is_weighted:
                        return True
                return False

        def isnt_frequent(self, target_stock_num):
                refer = {}
                for date in self.trading_amount_dic:
                        for stock in self.trading_amount_dic[date]:
                                try:  # 紀錄有上榜的股票在交易日中上榜的天數
                                        refer[stock[0]] += 1
                                except:
                                        refer[stock[0]] = 1
                threshold = round(len(self.date_list) * self.frequent_ratio)
                frequent_list = sorted(list(zip(refer.keys(), refer.values())), key=lambda x: x[1], reverse=True)
                
                # 採[(), ()]
                is_common = [stock[0] for stock in frequent_list if stock[1] >= threshold]
                if target_stock_num in is_common:
                        return False
                return True

        def isnt_fin_stock(self, target_stock_num):
                if target_stock_num[:2] != '28' or target_stock_num == '2897':
                        return True
                return False

        def is_rising(self, target_date, target_stock_num):
                stock_info = self.info_dic['stock_info'][target_stock_num][target_date]
                if stock_info[3] >= stock_info[4]:
                        return True
                return False
                
class b_fin_data_method(data_filter):
        def __init__(self, starttime, endtime, needed_info, parameter_dic):
                data_filter.__init__(self, starttime, endtime, needed_info)
                self.parameter_dic = parameter_dic

        def eps_and_pe(self, target_date, target_stock_num):
                # eps、pe
                needed_parameter = self.parameter_dic['eps_and_pe']
                type_of_method = needed_parameter['type_of_method']
                bigger_or_smaller = needed_parameter['bigger_or_smaller']
                amount = needed_parameter['amount']
                
                season_to_find = self.find_update_info(target_date, 'inc', target_stock_num)
                eps = info_dic['stock_inc_statement'][target_stock_num][season_to_find][-1]
                if type_of_method == 'eps':
                        if bigger_or_smaller == 'bigger':
                                if eps >= amount:
                                        return True
                                return False
                        else:
                                if eps < amount:
                                        return True
                                return False

                elif type_of_method == 'pe':
                        now_price = info_dic['stock_info'][target_stock_num][target_date][6]  # 收盤價
                        if bigger_or_smaller == 'bigger':
                                if eps >= amount:
                                        return True
                                return False
                        else:
                                if eps < amount:
                                        return True
                                return False

        def gross_margin(target_date, target_stock_num):
                needed_parameter = self.parameter_dic['gross_margin']
                bigger_or_smaller = needed_parameter['bigger_or_smaller']
                amount = needed_parameter['amount']

                season_to_find = self.find_update_info(target_date, 'inc', target_stock_num)
                first_row = info_dic['stock_inc_statement'][target_stock_num][season_to_find]['時間']
                gross_loc = first_row.index('營業毛利（毛損）')
                rev_loc = first_row.index('營業收入')

                now_data = info_dic['stock_inc_statement'][target_stock_num][season_to_find]
                gross_margin = now_data[gross_loc] / now_data[rev_loc] * 100  # 採%為單位
                if bigger_or_smaller == 'bigger':
                        if gross_margin >= amount:
                                return True
                        return False
                else:
                        if gross_margin < amount:
                                return True
                        return False

        def 

class s_price_method(data_filter):
        def __init__(self, starttime, endtime,  needed_info, n_days=3, profit_percentage=3, \
                     loss_percentage= -1.5):
                data_filter.__init__(self, starttime, endtime, needed_info)
                self.n_days_dic = {x:0 for x in self.stock_num_list}
                self.max_price_dic = {x:0 for x in self.stock_num_list}
                self.n_days = n_days
                self.profit_percentage = profit_percentage
                self.loss_percentage = loss_percentage

        def n_days_not_higher(self, target_date, target_stock_num):
                today_high = self.info_dic['stock_info'][target_stock_num][target_date][3]
                if today_high > self.max_price_dic[target_stock_num]:  # 若今天比過往紀錄高
                        self.max_price_dic[target_stock_num] = today_high
                        self.n_days_dic[target_stock_num] = 0
                else:
                        self.n_days_dic[target_stock_num] += 1

                if self.n_days_dic[target_stock_num] == self.n_days:
                        return self.info_dic['stock_info'][target_stock_num][target_date][5]
                return False

        def enough_profit_percentage(self, buy_in_price, target_date, target_stock_num):  # 3%停利
                today_high = self.info_dic['stock_info'][target_stock_num][target_date][3]

                if buy_in_price * (1 + self.profit_percentage/100) <= today_high:
                        return round(buy_in_price *(1 + self.profit_percentage/100), 1)
                return False

        def enough_loss_percentage(self, buy_in_price, target_date, target_stock_num):
                today_low = self.info_dic['stock_info'][target_stock_num][target_date][4]

                if buy_in_price * (1 + self.loss_percentage/100) >= today_low:
                        return round(buy_in_price *(1 + self.loss_percentage/100), 1)
                return False                

class data_evaluater(b_trading_amount_method, s_price_method):
        def __init__(self, starttime, endtime, needed_info, rank_num=30, higher_then_percent=0.4, frequent_ratio=0.5):
                b_trading_amount_method.__init__(self, starttime, endtime, needed_info, rank_num,\
                                                 higher_then_percent, frequent_ratio)
                s_price_method.__init__(self, starttime, endtime, needed_info)
                self.using_methods_dic = {'is_in_trading_amount': True, 'isnt_weighted': True, 'isnt_frequent': True, \
                                       'isnt_fin_stock': True, 'is_rising': True, 'enough_profit_percentage': True, \
                                       'n_days_not_higher': False, 'enough_loss_percentage': True}
                self.portfolio= {x: [] for x in self.stock_num_list}
                self.total_return_rate = 0
                self.winloss = [0, 0, 0]
                
        def daily_buy(self, target_date, target_stock_num):  # 用dic表達使用的方法
                result = set()
                if self.using_methods_dic['is_in_trading_amount']:
                        result.add(self.is_in_trading_amount(target_date, target_stock_num))

                if self.using_methods_dic['isnt_weighted']:
                        result.add(self.isnt_weighted(target_stock_num))

                if self.using_methods_dic['isnt_frequent']:
                        result.add(self.isnt_frequent(target_stock_num))

                if self.using_methods_dic['isnt_fin_stock']:
                        result.add(self.isnt_fin_stock(target_stock_num))

                if self.using_methods_dic['is_rising']:
                        result.add(self.is_rising(target_date, target_stock_num))

                if False not in result:
                        return True
                return False

        def daily_sell(self, buy_in_price, target_date, target_stock_num):
                result = []

                if self.using_methods_dic['enough_profit_percentage']:
                        result.append(('enough_profit_percentage', \
                                       self.enough_profit_percentage(buy_in_price, target_date, target_stock_num))) 
                        
                if self.using_methods_dic['enough_loss_percentage']:
                        result.append(('enough_loss_percentage', \
                                       self.enough_loss_percentage(buy_in_price, target_date, target_stock_num)))

                if self.using_methods_dic['n_days_not_higher']:
                        result.append(('n_days_not_higher', self.n_days_not_higher(target_date, target_stock_num)))
                
                refer = [x[1] for x in result]
                ending_price = self.info_dic['stock_info'][target_stock_num][target_date][5]
                refer2 = [x for x in refer if x != ending_price and x != False]
                refer3 = [x[0] for x in result if x[1] != False]
                if refer.count(False) < len(refer):  # 假設有要賣出
                        self.n_days_dic[target_stock_num] = 0
                        self.max_price_dic[target_stock_num] = 0
                        if refer2 == []:
                                return ending_price, refer3
                        else:
                                return refer2[0], refer3
                return False

        def simulating_trades(self, stock_num):
                for date in self.date_list:
                        refer_port = self.portfolio[stock_num]
                        l = len(refer_port)
                        if l != 0 and refer_port[-1][2] == 'b':
                                buying_price = refer_port[-1][1]
                                try:
                                        _ = self.daily_sell(buying_price, date, stock_num)
                                except KeyError:
                                        continue
                                if _ is not False:
                                        selling_price = _[0]
                                        selling_result = _[1]
                                                        
                                        return_rate = round((selling_price - buying_price)/buying_price, 4)
                                        self.portfolio[stock_num].append((date, selling_price, 's', selling_result, \
                                                                        return_rate))
                                        self.calculating_return(return_rate)
                        
                        if l == 0 or refer_port[-1][2] == 's':
                                if l != 0 and refer_port[-1][0] == date:
                                        continue
                                try:
                                        _ = self.daily_buy(date, stock_num)
                                except KeyError:
                                        continue
                                if _:
                                        buying_price = self.info_dic['stock_info'][stock_num][date][5]
                                        self.portfolio[stock_num].append((date, buying_price, 'b'))
                                        self.max_price_dic[stock_num] = self.info_dic['stock_info'][stock_num][date][3]
                                        # 若買進則將最高更新為買進日
        
        def calculating_return(self, return_rate):
                self.total_return_rate = round((self.total_return_rate + 1) * (return_rate + 1) - 1, 4)
                if return_rate > 0:
                        self.winloss[0] += 1
                elif return_rate < 0:
                        self.winloss[1] += 1
                else:
                        self.winloss[2] += 1

        def last_day_selling(self):
                last_day = self.date_list[-1]
                for stock in self.portfolio:
                        if self.portfolio[stock] != [] and self.portfolio[stock][-1][2] == 'b':
                                try:
                                        selling_price = self.info_dic['stock_info'][stock][last_day][5]
                                        buying_price = self.portfolio[stock][-1][1]
                                        return_rate = round((selling_price - buying_price)/buying_price, 3) 
                                        self.portfolio[stock].append((last_day, selling_price, 's', ['last_day_selling'], return_rate))
                                except KeyError:
                                        continue
                                                
        def displaying_result(self):
                for x in self.stock_num_list:
                        self.simulating_trades(x)
                self.last_day_selling()
                _ = round((self.total_return_rate + 1)**(1/sum(self.winloss)) - 1, 4)

                print(f'總報酬率: {round(self.total_return_rate, 4) * 100}%')
                print(f'勝負: {self.winloss}')
                print(f'單次報酬率: {_ * 100}%')
                        
                                        
a = data_evaluater('110/12', '111/08', ['stock_info', 'weighted_stock.csv'], 30, 0.4, 0.5)
a.displaying_result()
