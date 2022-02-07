# coding:utf-8

import requests
from fake_useragent import UserAgent
from selenium import webdriver
import time
import re
import pandas as pd

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_columns', None)


class StockAnalysis:
    _headers = {
        'User-Agent': '',
        'Host': ''
    }
    _ua = UserAgent(path="fake-useragent-0.1.11.json")

    def __init__(self):
        self.up_limit = None
        self.down_limit = None

    def up_down_limit(self):
        # 涨停板
        self.limit_get('up')
        # 跌停板
        # self.limit_get('down')

        # self.limit_print()

        self.limit_webrenew('./html/limit.html')

    def limit_get(self, order):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        if order == 'up':
            url_chip = '%E6%B6%A8%E5%81%9C%E6%9D%BF'
            nums_div = 19
            col_select = [(1, 4), (9, 10), (14, 18)]  # Customize
            columns = ['股票代码', '股票简称', '现价', '涨停原因', '开板次数', '流通市值', '几天几板', '涨停类型']  # Customize
        elif order == 'down':
            url_chip = '%E8%B7%8C%E5%81%9C%E6%9D%BF'
            nums_div = 17
            col_select = [(1, 7), (8, 9), (14, 16)]  # Customize
            columns = ['股票代码', '股票简称', '现价', '涨跌幅', '首次跌停时间', '最终跌停时间', '连续跌停天数', '跌停原因类型', '涨停类型']  # Customize
        else:
            return 'error'

        # 无头浏览器获取数据
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        opt.add_argument('--disable-gpu')
        wd = webdriver.Chrome(options=opt)

        url = f"http://www.iwencai.com/unifiedwap/result?w={url_chip}%EF%BC%9B%E9%9D%9Est%EF%BC%9B&querytype=stock"
        wd.get(url)
        print("selenium get successes!")

        time.sleep(1)
        xpath = '//*[@id="iwcTableWrapper"]/div[2]/div[2]'
        e = wd.find_element("xpath", xpath)
        e.click()
        print("selenium click1 successes!")

        time.sleep(1)
        xpath = '//*[@id="iwcTableWrapper"]/div[2]/div[2]/div/ul/li[3]'
        e = wd.find_element("xpath", xpath)
        e.click()
        print("selenium click2 successes!")

        time.sleep(2)
        xpath = '//*[@id="iwc-table-container"]/div[5]/div[1]/div[2]/table/tbody'
        raw_data = wd.find_element("xpath", xpath).text
        data_list = re.split('\n', raw_data)

        wd.quit()

        # 数据解析重组
        result_list = []
        nums = int(len(data_list) / nums_div)
        for i in range(nums):
            row_list = []
            for j in col_select:
                row_list.extend(data_list[i * nums_div + j[0]:i * nums_div + j[1]])
            result_list.append(row_list)

        index = [i for i in range(1, nums + 1)]

        if order == 'up':
            self.up_limit = pd.DataFrame(result_list, index=index, columns=columns)
        else:
            self.down_limit = pd.DataFrame(result_list, index=index, columns=columns)

    def limit_print(self):
        if self.up_limit is not None:
            print('-' * 30)
            print(self.up_limit)
        if self.down_limit is not None:
            print('-' * 30)
            print(self.down_limit)

    def limit_webrenew(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            data = f.read()

        limits = []
        if self.up_limit is not None:
            limits.append((self.up_limit, '涨停板'))
        if self.down_limit is not None:
            limits.append((self.down_limit, '跌停板'))

        ins = ''
        for limit in limits:
            ins += f'<caption>{limit[1]}</caption>\n\t\t<tr>'
            for i in limit[0].columns.tolist():
                ins += '<th>'
                ins += str(i)
                ins += '</th>'
            ins += '</tr>'
            for i in range(limit[0].shape[0]):
                ins += '\n\t\t<tr>'
                for j in limit[0].iloc[i].tolist():
                    ins += '<td>'
                    ins += str(j)
                    ins += '</td>'
                ins += '</tr>'

        new_data = re.sub('<table>(.*)</table>', f'<table>\n\t\t{ins}\n\t</table>', data, flags=re.S)

        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_data)

    @classmethod
    def _req_get(cls, url, host=None):
        cls._headers['User-Agent'] = cls._ua.random

        if host is None:
            cls._headers.pop('Host')
        else:
            cls._headers['Host'] = host

        return requests.get(url, headers=cls._headers)


def main():
    sa = StockAnalysis()
    sa.up_down_limit()


if __name__ == '__main__':
    main()
