# coding: utf-8

import os
from flask import Flask, request, render_template, flash
import mysqlx
import pymysql
import requests
from fake_useragent import UserAgent
import parsel
import time


class StockAnalysis:
    _headers = {
        'User-Agent': ''
    }
    _ua = UserAgent(path="code/fake-useragent-0.1.11.json")

    def __init__(self):
        self.mysql = {'host': 'localhost', 'port': 3306, 'user': 'root', 'passwd': '', 'db': 'mystock',
                      'charset': 'utf8'}
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

    def get_db_limits(self, limit_keys):
        conn = pymysql.connect(**self.mysql)
        cursor = conn.cursor()

        db_limits = []
        for i in limit_keys:
            cursor.execute("select * from stock_limits where limitKey = %s", i)
            db_limits.append(cursor.fetchone())

        conn.commit()
        cursor.close()
        conn.close()

        return db_limits

    def alter_db_limits(self, limits):
        conn = pymysql.connect(**self.mysql)
        cursor = conn.cursor()

        for limit in limits:
            cursor.execute("UPDATE stock_limits SET content = %s WHERE limitKey = %s", (limit[1], limit[0]))

        conn.commit()
        cursor.close()
        conn.close()

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


@app.route('/stock/discipline')
def discipline():
    return render_template('discipline.html')


@app.route('/stock/limit')
def limit():
    sa = StockAnalysis()

    db_last = sa.get_db_limits(['last'])
    laststamp = int(db_last[0][1])
    last = time.localtime(laststamp)
    nowstamp = int(time.time())
    now = time.localtime(nowstamp)

    # 判断是否需要更新
    if ((now.tm_wday < 5) and ((9 <= now.tm_hour <= 11) or (13 <= now.tm_hour <= 14))
        or (last.tm_wday < 5) and ((9 <= last.tm_hour <= 11) or (13 <= last.tm_hour <= 14))) \
            and (nowstamp - laststamp > 180):  # 需要
        sa.get_limit()

        db_limits = (('last', str(int(sa.renew_timestamp))), ('ZT', str(sa.up_limit)), ('DT', str(sa.down_limit)))
        sa.alter_db_limits(db_limits)

        return render_template('limit.html', upLimits=sa.up_limit,
                               downLimits=sa.down_limit,
                               renewTime=sa.renew_time)
    else:  # 不需要
        db_limits = sa.get_db_limits(('ZT', 'DT'))
        last_str_time = time.strftime("%Y-%m-%d %H:%M:%S", last)

        return render_template('limit.html', upLimits=eval(db_limits[0][1]),
                               downLimits=eval(db_limits[1][1]),
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

# 1645679301
