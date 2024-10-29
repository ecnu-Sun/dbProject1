import sqlite3
import pymongo

# 连接到 MongoDB
mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
mongo_db = mongo_client['bookstore']

# 定义 SQLite 和 MongoDB 数据库路径和集合名
databases = [
    {
        "sqlite_path": r'C:\Users\17314\Desktop\数据库project1\dbProject1\project1\bookstore\fe\data\book.db',
        "mongo_collection": mongo_db['books']
    }
    # {
    #     "sqlite_path": r'C:\Users\17314\Desktop\数据库project1\dbProject1\project1\bookstore\fe\data\book_lx.db',
    #     "mongo_collection": mongo_db['books_lx']
    # }
]

# 遍历每个数据库并执行迁移
for db in databases:
    # 连接到 SQLite 数据库
    sqlite_conn = sqlite3.connect(db["sqlite_path"])
    sqlite_cursor = sqlite_conn.cursor()

    # 查询 SQLite 数据
    sqlite_cursor.execute('SELECT * FROM book')
    rows = sqlite_cursor.fetchall()

    # 将数据插入到 MongoDB 指定的集合中
    for row in rows:
        db["mongo_collection"].insert_one({
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'publisher': row[3],
            'original_title': row[4],
            'translator': row[5],
            'pub_year': row[6],
            'pages': row[7],
            'price': row[8],
            'currency_unit': row[9],
            'binding': row[10],
            'isbn': row[11],
            'author_intro': row[12],
            'book_intro': row[13],
            'content': row[14],
            'tags': row[15],
            'picture': row[16],
        })

    # 关闭 SQLite 连接
    sqlite_conn.close()

# 关闭 MongoDB 连接
mongo_client.close()
