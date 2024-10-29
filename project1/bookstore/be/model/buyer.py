import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 用户id 书店id (书id和书数量)  主要返回  订单id
    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            # 判断用户id是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            
            # 判断书店id是否存在
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            # 创建订单号
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            # 对每本书判定 该书店是否有这本书
            for book_id, count in id_and_count:
                cursor = self.conn.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = ? AND book_id = ?;",
                    (store_id, book_id),
                )

                # 获取相关信息：库存 书本信息->价格
                row = cursor.fetchone() # 主键唯一
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                # 判断库存是否足够 
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 修改store对应条目 
                cursor = self.conn.execute(
                    "UPDATE store set stock_level = stock_level - ? "
                    "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                    (count, store_id, book_id, count),
                )
                # 双重保障，读取数据 与 更改数据 不是原子的，为了保证并发安全，需要再做检查。
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 对于每本书的购买，插入相关数据到 new_order_detail表中
                self.conn.execute(
                    "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                    "VALUES(?, ?, ?, ?);",
                    (uid, book_id, count, price),
                )
            # 对于这次订单，插入相关数据到 new_order表 中
            self.conn.execute(
                "INSERT INTO new_order(order_id, store_id, user_id) "
                "VALUES(?, ?, ?);",
                (uid, store_id, user_id),
            )

            self.conn.commit()
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    # 用户id 密码 订单id
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            # 判断订单是否存在
            cursor = conn.execute(
                "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
                (order_id,),
            )
            row = cursor.fetchone() # 主键唯一性

            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]

            # 防止 支付用户 与 下单用户 不匹配
            if buyer_id != user_id:
                return error.error_authorization_fail()

            # 获取 用户余额
            cursor = conn.execute(
                "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            )
            row = cursor.fetchone()

            # 判断 用户 是否存在
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]

            # 判断 用户密码 是否正确
            if password != row[1]:
                return error.error_authorization_fail()

            # 查找 书店店主 的 用户id
            cursor = conn.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
                (store_id,),
            )
            row = cursor.fetchone()

            # 判断 书店 是否还存在 或者书店与店主关联是否有误
            if row is None:
                return error.error_non_exist_store_id(store_id)

            #店主id
            seller_id = row[1]

            # 判断 店主id 是否存在
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # 获取本次订单的所有详细条目
            cursor = conn.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
                (order_id,),
            )
            total_price = 0

            # 计算总金额
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            # 逻辑上预检查，减少不必要的数据库操作
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # 这里检查是为了并发安全。所以无论如何都必须检查
            cursor = conn.execute(
                "UPDATE user set balance = balance - ?"
                "WHERE user_id = ? AND balance >= ?",
                (total_price, buyer_id, total_price),
            )
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            # 给店主账户打钱
            cursor = conn.execute(
                "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
                (total_price, seller_id),
            )
            # 例行检查
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(seller_id)

        # 删除已付款的订单
            cursor = conn.execute(
                "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)
            
            cursor = conn.execute(
                "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)
            conn.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    # 用户id 密码 充值的金额
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.execute(
                "SELECT password  from user where user_id=?", (user_id,)
            )
            row = cursor.fetchone()

            # 判断用户是否存在（这里的error是不是写错了？）
            if row is None:
                return error.error_authorization_fail()
            
            # 判断密码是否正确
            if row[0] != password:
                return error.error_authorization_fail()
            
            # 增加余额
            cursor = self.conn.execute(
                "UPDATE user SET balance = balance + ? WHERE user_id = ?",
                (add_value, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
