import pytest
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook
import uuid

class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_cancel_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        yield

    def test_cancel_order_success(self):
        # 生成一个订单
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False,max_book_count=5)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        # 成功取消订单
        code, message = self.buyer.cancel_order(order_id)
        assert code == 200
        assert message == "ok"

    def test_cancel_order_non_existent(self):
        # 尝试取消一个不存在的订单
        code, message = self.buyer.cancel_order("non_existent_order_id")
        assert code != 200

    def test_cancel_order_invalid_user(self):
        # 生成一个订单
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        # 修改用户 ID 来模拟无效用户
        self.buyer.user_id = self.buyer.user_id + "_invalid"
        code, message = self.buyer.cancel_order(order_id)
        assert code != 200
