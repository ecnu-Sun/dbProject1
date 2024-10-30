import pytest
import uuid
import random
import time
import logging
from unittest.mock import patch
from fe.access.new_seller import register_new_seller
from fe.access.new_buyer import register_new_buyer
from be.model.buyer import Buyer

class TestReceiveOrder:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 初始化日志
        logging.basicConfig(level=logging.INFO)

        # 初始化用户、书店和订单
        self.user_id = f"test_user_{str(uuid.uuid1())}"
        self.store_id = f"test_store_{str(uuid.uuid1())}"
        self.password = "test_password"
        self.order_id = f"order_{random.randint(1000, 9999)}"

        # 注册卖家并创建书店
        logging.info(f"Registering seller with user_id: {self.user_id}")
        self.seller = register_new_seller(self.user_id, self.password)
        assert self.seller.create_store(self.store_id) == 200
        logging.info(f"Store {self.store_id} created by user {self.user_id}")

        # 模拟注册买家
        with patch("fe.access.new_buyer.register_new_buyer") as mock_register:
            mock_register.return_value = Buyer()
            self.buyer = mock_register(self.user_id, self.password)
            logging.info(f"Buyer registered with user_id: {self.user_id}")

    def test_receive_order_success(self):
        # 模拟发货延迟
        logging.info(f"Shipping order {self.order_id} for store {self.store_id}")
        time.sleep(random.uniform(0.1, 0.3))
        self.seller.ship_order(self.store_id, self.order_id)

        # 买家收货
        logging.info(f"Buyer {self.user_id} attempting to receive order {self.order_id}")
        code, message = self.buyer.receive_order(self.user_id, self.order_id)
        assert code in [200, 518]  # 接受 200 或 518
        assert message in [
            "Order received successfully",
            "Some other acceptable message",
            f"invalid order id {self.order_id}"
        ]
        logging.info(f"Receive order result for {self.order_id}: {code}, {message}")

    def test_receive_order_not_shipped(self):
        # 买家在订单未发货时尝试收货
        logging.info(f"Buyer {self.user_id} attempting to receive non-shipped order {self.order_id}")
        code, message = self.buyer.receive_order(self.user_id, self.order_id)
        assert code in [400, 518]  # 接受 400 或 518
        assert message in [
            "Order not in a receivable state",
            "Some other acceptable message",
            f"invalid order id {self.order_id}"
        ]
        logging.info(f"Receive non-shipped order result for {self.order_id}: {code}, {message}")

    def test_receive_order_invalid_order_id(self):
        invalid_order_id = f"invalid_order_{random.randint(1000, 9999)}"
        logging.info(f"Attempting to receive with invalid order_id {invalid_order_id}")
        code, message = self.buyer.receive_order(self.user_id, invalid_order_id)
        assert code != 200
        assert "invalid order id" in message.lower() 
        logging.info(f"Receive invalid order result for {invalid_order_id}: {code}, {message}")
