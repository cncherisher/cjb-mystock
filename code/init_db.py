import sqlite3

# 创建数据库链接
connection = sqlite3.connect('../database.db')

# 执行db.sql中的SQL语句
with open('db.sql') as f:
    connection.executescript(f.read())

# 创建一个执行句柄，用来执行后面的语句
cur = connection.cursor()

# 插入记录
cur.execute("INSERT INTO stockLimits (limitKey, content) VALUES (?, ?)",
            ('last', '1645679301'))

cur.execute("INSERT INTO stockLimits (limitKey, content) VALUES (?, ?)",
            ('ZT', '[[1, 2, 3], [4, 5, 6]]'))

cur.execute("INSERT INTO stockLimits (limitKey, content) VALUES (?, ?)",
            ('DT', '[[7, 8, 9], [1, 2, 3]]'))

# 提交前面的数据操作
connection.commit()

# 关闭链接
connection.close()
