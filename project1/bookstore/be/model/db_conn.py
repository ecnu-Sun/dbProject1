from be.model import store

class DBConn:
    def __init__(self):
        # 获取 MongoDB 数据库连接
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        # 在 user 集合中查找用户ID
        user = self.conn['user'].find_one({"user_id": user_id})
        return user is not None  # 如果找到用户返回 True，否则返回 False

    def book_id_exist(self, store_id, book_id):
        # 在 store 集合的 books 数组中查找指定的书店ID和书籍ID
        store = self.conn['store'].find_one(
            {"store_id": store_id, "books.book_id": book_id}
        )
        return store is not None  # 如果找到书籍返回 True，否则返回 False

    def store_id_exist(self, store_id):
        # 在 store 集合中查找书店ID
        store = self.conn['store'].find_one({"store_id": store_id})
        return store is not None  # 如果找到书店返回 True，否则返回 False
