from be.model import db_conn
import logging
from pymongo.errors import PyMongoError


class Search(db_conn.DBConn):
    def __init__(self):
        super().__init__()

    def search_books(self, keywords: str, store_id: str = None, page: int = 1, page_size: int = 10):
        try:
            # 构建查询条件
            query = {'$text': {'$search': keywords}}

            if store_id:
                # 如果指定了 store_id，需要在该店铺的库存中查找
                store = self.conn['store'].find_one({'store_id': store_id})
                if not store:
                    return 513, f"non exist store id {store_id}", []

                # 获取该店铺的所有书籍ID
                book_ids_in_store = [book['book_id'] for book in store.get('books', [])]
                if not book_ids_in_store:
                    return 200, "ok", []  # 店铺中没有书籍

                # 在查询条件中增加 book_id 过滤
                query['book_id'] = {'$in': book_ids_in_store}

            # 分页
            skip = (page - 1) * page_size

            # 查询
            cursor = self.conn['book'].find(query).skip(skip).limit(page_size)

            # 收集结果
            results = list(cursor)

            return 200, "ok", results

        except PyMongoError as e:
            logging.error(f"Database error in search_books: {e}")
            return 528, f"{str(e)}", []
        except Exception as e:
            logging.error(f"Unexpected error in search_books: {e}")
            return 530, f"{str(e)}", []
