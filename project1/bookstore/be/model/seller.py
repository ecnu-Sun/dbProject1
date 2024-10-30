import json
from be.model import error
from be.model import db_conn
from pymongo.errors import PyMongoError
import logging
class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            # 检查用户和书店是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            # 检查书籍是否已经存在
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            # 将书籍信息转换为字典
            book_info = json.loads(book_json_str)

            # 插入新的书籍到 store 集合中的 books 数组
            self.conn["store"].update_one(
                {"store_id": store_id},
                {"$push": {"books": {
                    "book_id": book_id,
                    "book_info": book_info,
                    "stock_level": stock_level
                }}},
                upsert=True  # 如果不存在则创建新文档
            )
        except PyMongoError as e:
            logging.error(f"Database error in add_book: {e}", exc_info=True)
            return 528, f"{str(e)}"
        except Exception as e:
            return 530, f"{str(e)}"
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            # 检查用户、书店和书籍是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # 更新库存量
            update_result = self.conn["store"].update_one(
                {"store_id": store_id, "books.book_id": book_id},
                {"$inc": {"books.$.stock_level": add_stock_level}}
            )
            if update_result.matched_count == 0:
                return error.error_non_exist_book_id(book_id)
        except PyMongoError as e:
            return 528, f"{str(e)}"
        except Exception as e:
            return 530, f"{str(e)}"
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            # 检查用户是否存在以及书店ID是否已被使用
            if not self.user_id_exist(user_id):
                print("\n\n不存在user_id:"+user_id+"\n\n")
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 插入新书店到 store 集合
            store = {
                "store_id": store_id,
                "user_id": user_id,
                "books": []  # 初始状态为空
            }
            self.conn["store"].insert_one(store)
        except PyMongoError as e:
            return 528, f"{str(e)}"
        except Exception as e:
            return 530, f"{str(e)}"
        return 200, "ok"
