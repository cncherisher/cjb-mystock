# coding: utf-8

from flask import Flask, request, jsonify
from fake_useragent import UserAgent
import requests
import parsel


class FundAnalysis:
    _headers = {
        'User-Agent': ''
    }
    _ua = UserAgent(path="./conf/fake-useragent-0.1.11.json")

    def __init__(self, code):
        self.code = code
        self.s_hold = None

    def fund_check(self):
        url = f'http://fund.eastmoney.com/{self.code}.html'
        res = self._req_get(url)

        if res.status_code == 200:
            raw_data = res.text
            html_data = parsel.Selector(raw_data)
            list1 = html_data.xpath('//*[@id="position_shares"]/div[1]//text()').getall()
            raw_list = [i for i in list1 if (i[0] != ' ') and (i != '股吧') and (i != '相关资讯')]

            stock_hold = []
            for i in range(len(raw_list)):
                if i % 3 == 0:
                    stock_hold.append([raw_list[i]])
                else:
                    stock_hold[-1].append(raw_list[i])
            self.s_hold = stock_hold

            return 1
        else:
            return 0

    def web_display(self):
        if self.s_hold is not None:
            str_ins = f'\n\t<tr><th>{self.s_hold[0][0]}</th><th>{self.s_hold[0][1]}</th><th>{self.s_hold[0][2]}' \
                      f'</th></tr>'
            for i in self.s_hold[1:-1]:
                str_ins += f'\n\t<tr>'
                for j in i:
                    str_ins += f'<td>{j}</td>'
                str_ins += f'</tr>'

            str_web = f'<table>\n\t<caption>基金十大持仓股</caption>{str_ins}\n</table>'
            str_web += f'\n<p><span>{self.s_hold[-1][0]}</span><span>{self.s_hold[-1][1]}</span></p>'

            return str_web
        else:
            return "代码错误，请重新输入！"

    @classmethod
    def _req_get(cls, url):
        cls._headers['User-Agent'] = cls._ua.random
        res = requests.get(url, headers=cls._headers)
        res.encoding = 'utf-8'

        return res


# ---------------------------------------------------------------------


app = Flask(__name__)


@app.route('/test', methods=['POST'])
def index():
    fund_code = request.form.get('FundCode')
    fa = FundAnalysis(fund_code)
    fa.fund_check()

    return str(fa.web_display())


# ---------------------------------------------------------------------


# app = Flask(__name__)
#
#
# @app.route('/test')
# def index():
#     fund_code = 16172500
#     fa = FundAnalysis(fund_code)
#     fa.fund_check()
#
#     return str(fa.web_display())
#
#
# app.run()


# ---------------------------------------------------------------------


# str_ins = ''
# fund_code = 161725
# fa = FundAnalysis(fund_code)
# rs = fa.fund_check()
#
# str_ins += f'\n\t<tr><th>{rs[0][0]}</th><th>{rs[0][1]}</th><th>{rs[0][2]}</th></tr>'
# for i in rs[1:]:
#     str_ins += f'\n\t<tr>'
#     for j in i:
#         str_ins += f'<td>{j}</td>'
#     str_ins += f'</tr>'
#
# str_model = f'<table>\n\t<caption>基金十大持仓股</caption>{str_ins}\n</table>'
# print(str_model)

