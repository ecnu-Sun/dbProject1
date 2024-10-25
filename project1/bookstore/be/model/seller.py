from be.model import error
from be.db_conn import session
import json
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

class Seller:
    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            book_json = json.loads(book_json_str)
            # 检查用户、店铺和书籍ID是否存在
            if not user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            # 添加书籍信息
            book_one = Book(
                book_id=book_id,
                title=book_json.get("title"),
                author=book_json.get("author"),
                publisher=book_json.get("publisher"),
                original_title=book_json.get("original_title"),
                translator=book_json.get("translator"),
                pub_year=book_json.get("pub_year"),
                pages=book_json.get("pages"),
                original_price=book_json.get("price"),
                currency_unit=book_json.get("currency_unit"),
                binding=book_json.get("binding"),
                isbn=book_json.get("isbn"),
                author_intro=book_json.get("author_intro"),
                book_intro=book_json.get("book_intro"),
                content=book_json.get("content"),
                tags=book_json.get("tags"),
                picture=book_json.get("picture")
            )

            # 添加库存信息
            store_detail_one = Store_detail(
                store_id=store_id,
                book_id=book_id,
                stock_level=stock_level,
                price=book_json.get("price")
            )

            # 将数据写入数据库
            session.add(book_one)
            session.add(store_detail_one)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            return 528, f"Database error: {str(e)}"
        except json.JSONDecodeError:
            return 400, "Invalid book JSON format"
        except Exception as e:
            return 530, f"Unexpected error: {str(e)}"
        return 200, "Book added successfully"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            # 检查用户、店铺和书籍ID是否存在
            if not user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # 更新库存量
            store_detail = session.query(Store_detail).filter(
                and_(Store_detail.store_id == store_id, Store_detail.book_id == book_id)
            ).first()
            if store_detail:
                store_detail.stock_level += add_stock_level
                session.commit()
            else:
                return 404, "Store detail not found"
        except SQLAlchemyError as e:
            session.rollback()
            return 528, f"Database error: {str(e)}"
        except Exception as e:
            return 530, f"Unexpected error: {str(e)}"
        return 200, "Stock level updated successfully"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            # 检查用户和店铺ID是否存在
            if not user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 创建店铺记录
            store_one = Store(user_id=user_id, store_id=store_id)
            session.add(store_one)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            return 528, f"Database error: {str(e)}"
        except Exception as e:
            return 530, f"Unexpected error: {str(e)}"
        return 200, "Store created successfully"

    def send_books(self, seller_id: str, order_id: str):
        try:
            # 检查订单ID是否有效
            order = session.query(Order).filter(Order.order_id == order_id).first()
            if not order:
                return error.error_invalid_order_id(order_id)
            if order.status != 0:
                return 521, "Books have already been sent to the customer or the order is cancelled"

            # 检查店铺主是否是卖家
            store = session.query(Store).filter(Store.store_id == order.store_id).first()
            if not store or seller_id != store.user_id:
                return error.error_authorization_fail()

            # 更新订单状态
            order.status = 1
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            return 528, f"Database error: {str(e)}"
        except Exception as e:
            return 530, f"Unexpected error: {str(e)}"
        return 200, "Books sent successfully"
