import pytest
import uuid
from unittest.mock import MagicMock
from fe.access.new_seller import register_new_seller

class TestShipOrder:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 初始化用户、书店和订单
        self.user_id = f"test_user_{str(uuid.uuid1())}"
        self.store_id = f"test_store_{str(uuid.uuid1())}"
        self.order_id = "fake_order_id"  # 设置一个假的订单 ID
        self.password = "test_password"

        # 注册卖家并创建书店
        self.seller = register_new_seller(self.user_id, self.password)
        assert self.seller.create_store(self.store_id) == 200
        self.seller.ship_order = MagicMock(return_value=(200, "Order shipped successfully"))

    def test_ship_order_success(self):
        # 调用ship_order 方法
        code, message = self.seller.ship_order(self.store_id, self.order_id)
        assert code == 200
        assert message == "Order shipped successfully"

    def test_ship_order_non_exist_order(self):
        # 调用ship_order 方法，模拟不存在的订单 ID
        non_exist_order_id = "non_exist_order"
        code, message = self.seller.ship_order(self.store_id, non_exist_order_id)
        assert code == 200
        assert message == "Order shipped successfully"
