import re
import time


html_list = ['index.html', 'limit.html']

pat = '[?]v=[0-9]+'

for i in html_list:
    file_path = '../html/' + i

    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()

    new_data = re.sub(pat, f'?v={int(time.time())}', data)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_data)

