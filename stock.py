# coding: utf-8

import os
from flask import Flask, request, render_template, flash
import sqlite3
import requests
from fake_useragent import UserAgent
import parsel
import time


def get_db_connection():
    # 创建数据库链接到database.db文件
    conn = sqlite3.connect('database.db')
    # 设置数据的解析方法，有了这个设置，就可以像字典一样访问每一列数据
    conn.row_factory = sqlite3.Row
    return conn


def get_db_limit(limit_key):
    conn = get_db_connection()
    db_limit = conn.execute('SELECT * FROM stockLimits WHERE limitKey = ?', (limit_key,)).fetchone()
    conn.close()
    return db_limit


class StockAnalysis:
    _headers = {
        'User-Agent': ''
    }
    _ua = UserAgent(path="code/fake-useragent-0.1.11.json")

    def __init__(self):
        self.renew_timestamp = None
        self.renew_time = None
        self.up_limit = None
        self.down_limit = None

    def get_limit(self):
        for limit in [['ZT', 'fbt%3Aasc', ['c', 'n', 'zdp', 'p', 'hs', 'zbc', 'lbc', 'hybk']],
                      ['DT', 'lbt%3Adesc', ['c', 'n', 'zdp', 'p', 'hs', 'days', 'oc', 'hybk']]]:
            get_type = limit[0]
            sort_type = limit[1]
            keys = limit[2]

            self.renew_timestamp = time.time()
            renew_struct_time = time.localtime(self.renew_timestamp)
            self.renew_time = time.strftime("%Y-%m-%d %H:%M:%S", renew_struct_time)

            url = f'http://push2ex.eastmoney.com/getTopic{get_type}Pool' \
                  f'?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt' \
                  f'&Pageindex=0&pagesize=170&sort={sort_type}' \
                  f'&date={time.strftime("%Y%m%d", renew_struct_time)}' \
                  f'&_={int(self.renew_timestamp * 1000)}'

            data = self._req_get(url).json()

            stocks = []
            for i in range(data['data']['tc']):
                stock = [i]
                for key in keys:
                    if key == 'zdp' or key == 'hs':
                        cont = f"{round(data['data']['pool'][i][key], 2)}%"
                    elif key == 'p':
                        cont = round(data['data']['pool'][i][key] / 1000, 2)
                    else:
                        cont = data['data']['pool'][i][key]
                    stock.append(cont)
                stocks.append(stock)

            if get_type == 'ZT':
                self.up_limit = stocks
            else:
                self.down_limit = stocks

    @classmethod
    def _req_get(cls, url):
        cls._headers['User-Agent'] = cls._ua.random
        res = requests.get(url, headers=cls._headers)
        res.encoding = 'utf-8'

        return res


class FundAnalysis:
    _headers = {
        'User-Agent': ''
    }
    _ua = UserAgent(path="code/fake-useragent-0.1.11.json")

    def __init__(self, code):
        self.code = code
        self.stock_hold = None

    def fund_hold(self):
        url = f'http://fund.eastmoney.com/{self.code}.html'
        res = self._req_get(url)

        if res.status_code == 200:
            raw_data = res.text
            html_data = parsel.Selector(raw_data)
            raw_list = html_data.xpath(
                '//*[@id="position_shares"]/div[1]//text()').getall()
            raw_list = [i for i in raw_list if (
                    i[0] != ' ') and (i != '股吧') and (i != '相关资讯')]

            hold_th = raw_list[0:3]
            hold_tds = raw_list[3:-2]
            hold_tds = [[hold_tds[i * 3], hold_tds[i * 3 + 1],
                         hold_tds[i * 3 + 2]] for i in range(len(hold_tds) // 3)]
            hold_p = raw_list[-2:]

            self.stock_hold = (hold_th, hold_tds, hold_p)

            return 1
        else:
            return 0

    @classmethod
    def _req_get(cls, url):
        cls._headers['User-Agent'] = cls._ua.random
        res = requests.get(url, headers=cls._headers)
        res.encoding = 'utf-8'

        return res


# ---------------------------------------------------------------------


template_path = os.path.abspath('html')
app = Flask(__name__, template_folder=template_path)


@app.route('/stock')
def index():
    return render_template('index.html')


@app.route('/stock/limit')
def limit():
    limit_last = get_db_limit('last')
    laststamp = int(limit_last['content'])
    last = time.localtime(laststamp)
    nowstamp = int(time.time())
    now = time.localtime(nowstamp)

    # 判断是否需要更新
    if ((now.tm_wday < 5) and ((9 <= now.tm_hour <= 12) or (13 <= now.tm_hour <= 15))
        or (last.tm_wday < 5) and ((9 <= last.tm_hour <= 12) or (13 <= last.tm_hour <= 15))) \
            and (nowstamp - laststamp > 180):  # 需要
        sa = StockAnalysis()
        sa.get_limit()

        conn = get_db_connection()
        conn.execute('UPDATE stockLimits SET content = ?'
                     ' WHERE limitKey = ?',
                     (str(int(sa.renew_timestamp)), 'last'))
        conn.execute('UPDATE stockLimits SET content = ?'
                     ' WHERE limitKey = ?',
                     (str(sa.up_limit), 'ZT'))
        conn.execute('UPDATE stockLimits SET content = ?'
                     ' WHERE limitKey = ?',
                     (str(sa.down_limit), 'DT'))
        conn.commit()
        conn.close()

        return render_template('limit.html', upLimits=sa.up_limit,
                               downLimits=sa.down_limit,
                               renewTime=sa.renew_time)
    else:  # 不需要
        up_limit = get_db_limit('ZT')
        down_limit = get_db_limit('DT')
        last_str_time = time.strftime("%Y-%m-%d %H:%M:%S", last)

        return render_template('limit.html', upLimits=eval(up_limit['content']),
                               downLimits=eval(down_limit['content']),
                               renewTime=last_str_time)


@app.route('/stock/fundAnalysis', methods=['GET', 'POST'])
def fund_analysis():
    if request.method == 'POST':
        fund_code = request.form.get('fund-code')
        fa = FundAnalysis(fund_code)

        if fa.fund_hold() == 1:
            return render_template('fundAnalysis.html', stockHoldTh=fa.stock_hold[0],
                                   stockHoldTds=fa.stock_hold[1], stockHoldP=fa.stock_hold[2])
        else:
            return "代码错误，请重新输入！"  # TODO:

    return render_template('fundCode.html')


# app.run()

