import sqlite3
from pymongo import MongoClient
import base64

sqlite_conn = sqlite3.connect('fe/data/book.db')
sqlite_cursor = sqlite_conn.cursor()

mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['bookstore']  # 您可以根据需要更改数据库名称
mongo_collection = mongo_db['books']  # 集合名称

sqlite_cursor.execute("SELECT * FROM book")
rows = sqlite_cursor.fetchall()

column_names = [description[0] for description in sqlite_cursor.description]

# 遍历每一行并插入到 MongoDB
for row in rows:
    book = {}
    for idx, value in enumerate(row):
        column = column_names[idx]
        if column == 'picture' and value is not None:
            book[column] = base64.b64encode(value).decode('utf-8')
        else:
            book[column] = value

    mongo_collection.insert_one(book)

print("数据迁移完成！")

# 关闭连接
sqlite_conn.close()
mongo_client.close()
