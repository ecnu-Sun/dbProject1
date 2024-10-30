import pytest
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.test.gen_book_data import GenBook
import uuid

class TestOrderHistory:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_history_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_history_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_history_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        yield

    def test_empty_order_history(self):
        # 查询没有订单的历史
        code, message, orders = self.buyer.order_history()
        assert code == 200
        assert len(orders) == 0

    def test_order_history_with_orders(self):
        # 生成订单并检查订单历史
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False,max_book_count=5)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        # 检查订单是否出现在历史中
        code, message, orders = self.buyer.order_history()
        assert code == 200
        assert any(order["order_id"] == order_id for order in orders)

    def test_order_history_invalid_user(self):
        # 用一个不存在的用户 ID 查询订单历史
        self.buyer.user_id = self.buyer.user_id + "_invalid"
        code, message, orders = self.buyer.order_history()
        assert code != 200
