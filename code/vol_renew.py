import os
import re
import time


t = int(time.time())
pat = '-v=[0-9]+'
css_list = os.listdir('../static/stock-css')
js_list = os.listdir('../static/stock-js')


for i in css_list:
    new_name = re.sub(pat, f'-v={t}', i)
    os.rename(f'../static/stock-css/{i}', f'../static/stock-css/{new_name}')

for i in js_list:
    new_name = re.sub(pat, f'-v={t}', i)
    os.rename(f'../static/stock-js/{i}', f'../static/stock-js/{new_name}')


html_list = ['base.html', 'fundCode.html']

for i in html_list:
    file_path = '../html/' + i

    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()

    new_data = re.sub(pat, f'-v={t}', data)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_data)


