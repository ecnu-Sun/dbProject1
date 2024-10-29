import uuid
import logging
from be.model import db_conn
from be.model import error
from pymongo.errors import PyMongoError

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 用户id ，书店id ，(书id和书数量)；主要返回订单id
    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
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
            items = []  # 存储订单详情
            total_price = 0

            # 对每本书判定该书店是否有这本书，并获取库存、价格
            for book_id, count in id_and_count:
                book = self.conn["store"].find_one({"store_id": store_id, "books.book_id": book_id}, 
                                                    {"books.$": 1})
                if book is None or not book.get("books"):
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                book_info = book["books"][0]
                stock_level = book_info["stock_level"]
                price = book_info["book_info"]["price"]

                # 判断库存是否足够
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 减少库存
                update_result = self.conn["store"].update_one(
                    {"store_id": store_id, "books.book_id": book_id, "books.stock_level": {"$gte": count}},
                    {"$inc": {"books.$.stock_level": -count}}
                )
                if update_result.matched_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 添加订单详细信息
                items.append({"book_id": book_id, "count": count, "price": price})
                total_price += price * count

            # 插入新订单到 new_order 集合
            order = {
                "order_id": uid,
                "user_id": user_id,
                "store_id": store_id,
                "items": items,
                "total_price": total_price
            }
            self.conn["new_order"].insert_one(order)
            order_id = uid
        except PyMongoError as e:
            logging.error(f"Database error: {e}")
            return 528, f"{str(e)}", ""
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return 530, f"{str(e)}", ""

        return 200, "ok", order_id

    # 用户id 密码 订单id
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            # 判断订单是否存在
            order = self.conn["new_order"].find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = order["user_id"]
            store_id = order["store_id"]

            # 防止支付用户与下单用户不匹配
            if buyer_id != user_id:
                return error.error_authorization_fail()

            # 获取用户信息
            user = self.conn["user"].find_one({"user_id": buyer_id})
            if user is None:
                return error.error_non_exist_user_id(buyer_id)

            # 判断用户密码是否正确
            if password != user["password"]:
                return error.error_authorization_fail()

            balance = user["balance"]

            # 查找书店的店主
            store = self.conn["store"].find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = store["user_id"]

            # 判断店主id是否存在
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # 计算订单总金额
            total_price = order["total_price"]
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # 更新买家余额
            update_result = self.conn["user"].update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
            if update_result.matched_count == 0:
                return error.error_not_sufficient_funds(order_id)

            # 给店主增加余额
            self.conn["user"].update_one(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )

            # 删除已付款订单
            self.conn["new_order"].delete_one({"order_id": order_id})
        except PyMongoError as e:
            logging.error(f"Database error: {e}")
            return 528, f"{str(e)}"
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return 530, f"{str(e)}"

        return 200, "ok"

    # 用户id 密码 充值的金额
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            # 查询用户信息
            user = self.conn["user"].find_one({"user_id": user_id})
            if user is None:
                return error.error_non_exist_user_id(user_id)

            # 检查密码是否正确
            if user["password"] != password:
                return error.error_authorization_fail()

            # 更新用户余额
            update_result = self.conn["user"].update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
            if update_result.matched_count == 0:
                return error.error_non_exist_user_id(user_id)
        except PyMongoError as e:
            logging.error(f"Database error: {e}")
            return 528, f"{str(e)}"
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return 530, f"{str(e)}"

        return 200, "ok"
