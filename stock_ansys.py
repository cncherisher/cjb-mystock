# coding:utf-8

import requests
from fake_useragent import UserAgent
from selenium import webdriver
import time
import re
import pandas as pd

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_columns', None)


class Review:
    _headers = {
        'User-Agent': '',
        'Host': ''
    }
    _ua = UserAgent(path="fake-useragent-0.1.11.json")

    def __init__(self):
        pass

    def up_down_limit(self):
        # 涨停板
        up_limit = self.limit_get(1)
        # 跌停板
        # down_limit = self.limit_get(0)

        # self.limit_print(up_limit)
        self.limit_webrenew(up_limit)
        # self.limit_print(down_limit)

    @staticmethod
    def limit_get(order):
        if order == 1:
            url_chip = '%E6%B6%A8%E5%81%9C%E6%9D%BF'
            nums_div = 19
            col_select = [(1, 7), (9, 10), (14, 18)]
            columns = ['股票代码', '股票简称', '现价', '涨跌幅', '首次涨停时间', '最终涨停时间', '涨停原因', '开板次数', '流通市值', '几天几板', '涨停类型']
        elif order == 0:
            url_chip = '%E8%B7%8C%E5%81%9C%E6%9D%BF'
            nums_div = 17
            col_select = [(1, 7), (8, 9), (14, 16)]
            columns = ['股票代码', '股票简称', '现价', '涨跌幅', '首次跌停时间', '最终跌停时间', '连续跌停天数', '跌停原因类型', '涨停类型']
        else:
            return 'error'

        # 无头浏览器获取数据
        opt = webdriver.ChromeOptions()
        opt.headless = True
        wd = webdriver.Chrome(options=opt)

        url = f"http://www.iwencai.com/unifiedwap/result?w={url_chip}%EF%BC%9B%E9%9D%9Est%EF%BC%9B&querytype=stock"
        wd.get(url)
        print("selenium get successes!")

        time.sleep(1)
        xpath = '//*[@id="iwcTableWrapper"]/div[2]/div[2]'
        e = wd.find_element_by_xpath(xpath)
        e.click()
        print("selenium click1 successes!")

        time.sleep(1)
        xpath = '//*[@id="iwcTableWrapper"]/div[2]/div[2]/div/ul/li[3]'
        e = wd.find_element_by_xpath(xpath)
        e.click()
        print("selenium click2 successes!")

        time.sleep(1)
        xpath = '//*[@id="iwc-table-container"]/div[5]/div[1]/div[2]/table/tbody'
        raw_data = wd.find_element_by_xpath(xpath).text
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
        limit_df = pd.DataFrame(result_list, index=index, columns=columns)

        return limit_df

    @staticmethod
    def limit_print(limit_list):
        print('-' * 30)
        print(limit_list)

    @staticmethod
    def limit_webrenew(limit_list):
        with open('./html/limit.html', 'r', encoding='utf-8') as f:
            data = f.read()

        ins = '<tr>'
        for i in limit_list.columns.tolist():
            ins += '<th>'
            ins += str(i)
            ins += '</th>'
        ins += '</tr>'
        for i in range(limit_list.shape[0]):
            ins += '\n\t\t<tr>'
            for j in limit_list.iloc[i].tolist():
                ins += '<td>'
                ins += str(j)
                ins += '</td>'
            ins += '</tr>'

        new_data = re.sub('</caption>(.*)</table>', f'</caption>\n\t\t{ins}\n\t</table>', data, flags=re.S)

        with open('./html/limit.html', 'w', encoding='utf-8') as f:
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
    r = Review()
    r.up_down_limit()


if __name__ == '__main__':
    main()
