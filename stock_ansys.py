# coding:utf-8

# import requests
# from fake_useragent import UserAgent
from selenium import webdriver
import time
import re
import pandas as pd
from collections import Counter
from apscheduler.schedulers.blocking import BlockingScheduler

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_columns', None)


class StockAnalysis:
    # _headers = {
    #     'User-Agent': '',
    #     'Host': ''
    # }
    # _ua = UserAgent(path="fake-useragent-0.1.11.json")

    def __init__(self):
        self.limit_renew_time = ''
        self.up_limit = None
        self.up_limit_keys = None
        self.down_limit = None
        self.down_limit_keys = None

    def up_down_limit(self):
        # 涨停板
        self.limit_get('up')
        # 跌停板
        # self.limit_get('down')

        # self.limit_print()
        self.limit_webrenew('./html/limit.html')

    def limit_get(self, order):
        self.limit_renew_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(self.limit_renew_time)
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
        print("selenium get succeeded!")

        # TODO: 解决网页未加载完成的问题
        time.sleep(1)
        xpath = '//*[@id="iwcTableWrapper"]/div[2]/div[2]'
        e = wd.find_element("xpath", xpath)
        e.click()
        print("selenium click1 succeeded!")

        time.sleep(1)
        xpath = '//*[@id="iwcTableWrapper"]/div[2]/div[2]/div/ul/li[3]'
        e = wd.find_element("xpath", xpath)
        e.click()
        print("selenium click2 succeeded!")

        time.sleep(3)
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
        elif order == 'down':
            self.down_limit = pd.DataFrame(result_list, index=index, columns=columns)

        print('limit process succeeded')

        # 处理关键词
        if order == 'up':
            keys_list1 = self.up_limit.loc[:, '涨停原因'].tolist()
            keys_list2 = []
            for i in keys_list1:
                keys_list2.extend(re.split("[+]", i))
            self.up_limit_keys = Counter(keys_list2).most_common()

        print('limit keys process succeeded')

        return 'successful'

    # def limit_print(self):
    #     if self.up_limit is not None:
    #         print('-' * 30)
    #         print(self.up_limit)
    #     if self.down_limit is not None:
    #         print('-' * 30)
    #         print(self.down_limit)

    def limit_webrenew(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            data = f.read()

        # 1. 涨跌停板 TODO: 补跌停板的
        limits = []
        if self.up_limit is not None:
            limits.append((self.up_limit, '涨停板'))
        if self.down_limit is not None:
            limits.append((self.down_limit, '跌停板'))

        ins = ''
        for limit in limits:
            ins += f'\n\t\t\t<caption>{limit[1]}  更新时间：{self.limit_renew_time}</caption>\n\t\t\t<tr>'
            for i in limit[0].columns.tolist():
                ins += f'<th>{str(i)}</th>'
            ins += '</tr>'
            for i in range(limit[0].shape[0]):
                ins += '\n\t\t\t<tr>'
                for j in limit[0].iloc[i].tolist():
                    ins += f'<td>{str(j)}</td>'
                ins += '</tr>'

        new_data = re.sub('<table id="upLimit">(.*?)</table>', f'<table id="upLimit">{ins}\n\t\t</table>',
                          data, flags=re.S)

        # 2. 涨跌停板关键词 TODO: 补跌停板的关键词
        limits = []
        if self.up_limit_keys is not None:
            limits.append((self.up_limit_keys, '涨停板关键词'))
        if self.down_limit_keys is not None:
            limits.append((self.down_limit_keys, '跌停板关键词'))

        ins = ''
        for limit in limits:
            ins += f'\n\t\t\t<caption>{limit[1]}</caption>\n\t\t\t<tr><th>关键词</th><th>次数</th></tr>'
            for i in limit[0]:
                ins += f'\n\t\t\t<tr><td>{i[0]}</td><td>{i[1]}</td></tr>'

        new_data = re.sub('<table id="upLimitKeys">(.*?)</table>', f'<table id="upLimitKeys">{ins}\n\t\t</table>',
                          new_data, flags=re.S)

        # 保存
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_data)

    # @classmethod
    # def _req_get(cls, url, host=None):
    #     cls._headers['User-Agent'] = cls._ua.random
    #
    #     if host is None:
    #         cls._headers.pop('Host')
    #     else:
    #         cls._headers['Host'] = host
    #
    #     return requests.get(url, headers=cls._headers)


def ctrl_task1(scheduler, sa):
    global ctrl_flag
    if ctrl_flag == 0:
        print('开盘开盘！！！')
        scheduler.add_job(func=task, args=(sa,), trigger='interval', id='task', minutes=5)
        ctrl_flag = 1
    else:
        print('中午休市，下午再战！')
        scheduler.remove_job('task')
        ctrl_flag = 0
        scheduler.resume_job('ctrl_task2')
        scheduler.pause_job('ctrl_task1')


def ctrl_task2(scheduler, sa):
    global ctrl_flag
    if ctrl_flag == 0:
        print('开盘开盘！！！')
        scheduler.add_job(func=task, args=(sa,), trigger='interval', id='task', minutes=5)
        ctrl_flag = 1
    else:
        print('休市休市，明天再战！')
        scheduler.remove_job('task')
        ctrl_flag = 0
        scheduler.resume_job('ctrl_task1')
        scheduler.pause_job('ctrl_task2')


def task(sa):
    sa.up_down_limit()


def main():
    sa = StockAnalysis()
    # task(sa)
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    # scheduler.add_job(func=task, args=(sa,), trigger='interval', id='task', minutes=5)
    scheduler.add_job(func=ctrl_task1, args=(scheduler, sa), trigger='cron', id='ctrl_task1',
                      day_of_week='mon-fri', hour='9, 11', minute=30)
    scheduler.add_job(func=ctrl_task2, args=(scheduler, sa), trigger='cron', id='ctrl_task2',
                      day_of_week='mon-fri', hour='13, 15')
    scheduler.pause_job('ctrl_task2')
    scheduler.start()


if __name__ == '__main__':
    ctrl_flag = 0
    main()
