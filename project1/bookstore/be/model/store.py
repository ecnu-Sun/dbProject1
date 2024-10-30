# import logging
# import threading
# from pymongo import MongoClient, errors
#
# class Store:
#     def __init__(self):
#         # 连接到 MongoDB 数据库
#         self.client = MongoClient('mongodb://localhost:27017')
#         self.db = self.client['bookstore']
#         self.init_collections()  # 初始化集合结构
#
#     def init_collections(self):
#         try:
#             # 创建集合
#             self.db.create_collection("user", capped=False)
#             self.db.create_collection("store", capped=False)
#             self.db.create_collection("new_order", capped=False)
#
#             # 初始化 user 集合
#             self.db['user'].create_index("user_id", unique=True)
#
#             # 初始化 store 集合
#             # 创建 store_id 和 book_id 的复合唯一索引，防止重复存储同一书店的同一书籍
#             self.db['store'].create_index([("store_id", 1), ("books.book_id", 1)], unique=True)
#
#             # 初始化 order 集合
#             # 为 order_id 创建唯一索引
#             self.db['new_order'].create_index("order_id", unique=True)
#             self.db['new_order'].create_index([("items.book_id", 1), ("order_id", 1)], unique=True)
#             logging.info("MongoDB collections and indexes are initialized.")
#         except errors.PyMongoError as e:
#             logging.error(f"Error initializing MongoDB collections: {e}")
#         except errors.CollectionInvalid:
#             logging.warning("Collection already exists.")
#
#     def get_db_conn(self):
#         # 返回 MongoDB 数据库实例
#         return self.db
#
#
# # 全局变量和事件
# database_instance: Store = None
# init_completed_event = threading.Event()
#
# def init_database():
#     global database_instance
#     database_instance = Store()
#     init_completed_event.set()  # 标记数据库初始化完成
#
# def get_db_conn():
#     global database_instance
#     return database_instance.get_db_conn()  # 返回数据库实例
import logging
import threading
from pymongo import MongoClient, errors

class Store:
    def __init__(self):
        # 连接到 MongoDB 数据库
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['bookstore']
        self.init_collections()  # 初始化集合结构

    def init_collections(self):
        try:
            # 检查并创建集合
            collections = ['user', 'store', 'new_order', 'book']
            existing_collections = self.db.list_collection_names()
            for collection_name in collections:
                if collection_name not in existing_collections:
                    self.db.create_collection(collection_name)

            # 为集合创建索引
            self.db['user'].create_index('user_id', unique=True)
            self.db['store'].create_index([('store_id', 1), ('books.book_id', 1)], unique=True)
            self.db['new_order'].create_index('order_id', unique=True)
            self.db['new_order'].create_index([('items.book_id', 1), ('order_id', 1)], unique=True)

            # 为 book 集合创建全文索引
            indexes = self.db['book'].index_information()
            if 'book_full_text_index' not in indexes:
                self.db['book'].create_index(
                    [
                        ('title', 'text'),
                        ('tags', 'text'),
                        ('catalog', 'text'),
                        ('content', 'text')
                    ],
                    name='book_full_text_index'
                )
            logging.info("MongoDB collections and indexes are initialized.")
        except errors.PyMongoError as e:
            logging.error(f"Error initializing MongoDB collections: {e}")

    def get_db_conn(self):
        # 返回 MongoDB 数据库实例
        return self.db

# 全局变量和事件
database_instance: Store = None
init_completed_event = threading.Event()

def init_database():
    global database_instance
    database_instance = Store()
    init_completed_event.set()  # 标记数据库初始化完成

def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()  # 返回数据库实例

