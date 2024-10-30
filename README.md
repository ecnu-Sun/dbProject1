# CDMS.Xuan_ZHOU.2024Fall.DaSE

## 运行整体流程

在一次标准的测试流程中，首先搜索当前文件树下符合规则（以 test_ 开头、以 _test 结尾或位于 /fe/bench 目录）的测试文件。测试文件被调用后会触发前端逻辑，通过 /fe/access 向后端发送 HTTP 指令。后端接收指令后，通过 /be/view 中的函数解析 HTTP 参数并执行解析得到的指令，最终调用 /be/model 中的对应函数完成操作。

## 基础功能

### 卖家创建店铺
先判断卖家的用户ID或店铺是否存在
```python
if not self.user_id_exist(user_id):
    print("\n\n不存在user_id:"+user_id+"\n\n")
    return error.error_non_exist_user_id(user_id)
if self.store_id_exist(store_id):
    return error.error_exist_store_id(store_id)
``` 

如果用户ID存在且店铺不存在，则把这数据插入
```python
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
```

这个文件对应test_create_store.py文件，两个测试用例：test_ok和test_error_exist_store_id。test_ok会注册一个新用户并以该用户创建一个店铺；test_error_exist_store_id创建一次同一个店铺，用于测试创建已经存在的店铺时是否成功报错。



### 卖家在店铺中添加书籍信息
要确保userid，storeid，bookid都存在
```python
# 检查用户和书店是否存在
if not self.user_id_exist(user_id):
    return error.error_non_exist_user_id(user_id)
if not self.store_id_exist(store_id):
    return error.error_non_exist_store_id(store_id)

# 检查书籍是否已经存在
if self.book_id_exist(store_id, book_id):
    return error.error_exist_book_id(book_id)
```

将数据插入
```python
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

        # 插入书籍到 book 集合
        self.conn['book'].update_one(
            {'book_id': book_id},
            {'$set': {
                'book_id': book_id,
                'title': book_info.get('title', ''),
                'tags': book_info.get('tags', []),
                'catalog': book_info.get('catalog', ''),
                'content': book_info.get('content', ''),
                'book_info': book_info
            }},
            upsert=True
        )
    except PyMongoError as e:
        logging.error(f"Database error in add_book: {e}", exc_info=True)
        return 528, f"{str(e)}"
    except Exception as e:
        return 530, f"{str(e)}"
    return 200, "ok"
```
这个函数对应test_add_book文件。test_ok测试基本功能，test_error_non_exist_store_id、test_error_exist_book_id和test_error_non_exist_user_id分别测试店铺、书籍、卖家不存在时系统是否报错。

### 卖家增加库存
确保卖家、店铺、添加的图书都存在
```python
if not self.user_id_exist(user_id):
    return error.error_non_exist_user_id(user_id)
if not self.store_id_exist(store_id):
    return error.error_non_exist_store_id(store_id)
if not self.book_id_exist(store_id, book_id):
    return error.error_non_exist_book_id(book_id)
```

对库存数量进行加操作
```python
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
```

卖家增加库存函数对应test_add_stock_level文件，test_ok测试接口基本功能，test_error_non_exist_store_id、test_error_exist_book_id和test_error_non_exist_user_id分别用于测试店铺、书籍、卖家不存在时系统是否报错。


## 额外功能

### 发货功能
ship_order 将指定订单的状态更新为“已发货”。首先检查用户、书店和订单是否存在，然后在数据库中查找符合条件的订单，将其状态更新为“已发货”。如果一切正常，返回成功消息；如果发生错误（如订单不存在或数据库问题），则返回相应的错误信息。
```python
def ship_order(self, user_id: str, store_id: str, order_id: str) -> (int, str):
    try:
        # 检查用户、书店和订单是否存在
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if not self.order_id_exist(order_id):  # 假设有 order_id_exist 方法来检查订单
            return error.error_non_exist_order_id(order_id)

        # 更新订单状态为“已发货”
        update_result = self.conn["orders"].update_one(
            {"order_id": order_id, "store_id": store_id, "user_id": user_id},
            {"$set": {"status": "shipped"}}
        )
        if update_result.matched_count == 0:
            return error.error_non_exist_order_id(order_id)
    except PyMongoError as e:
        logging.error(f"Database error in ship_order: {e}", exc_info=True)
        return 528, f"{str(e)}"
    except Exception as e:
        return 530, f"{str(e)}"
    return 200, "Order shipped successfully"
```

#### 发货功能后端接口
用POST
```python
@bp_seller.route("/ship_order", methods=["POST"])
def ship_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    order_id: str = request.json.get("order_id")

    s = seller.Seller()
    code, message = s.ship_order(user_id, store_id, order_id)

    return jsonify({"message": message}), code
```
#### 发货功能测试
TestShipOrder 类用于验证订单发货功能。它在 setup 方法中初始化测试所需的用户、书店和订单，并模拟买家下单。test_ship_order_success 测试订单成功发货的情况，断言返回状态码为 200，且消息为“Order shipped successfully”。test_ship_order_non_exist_order 测试发货时订单不存在的情况，断言状态码非 200，且消息提示订单 ID 不存在。
```python
class TestShipOrder:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 初始化用户、书店和订单
        self.user_id = f"test_user_{str(uuid.uuid1())}"
        self.store_id = f"test_store_{str(uuid.uuid1())}"
        self.order_id = f"test_order_{str(uuid.uuid1())}"
        self.password = "test_password"

        # 注册卖家并创建书店
        self.seller = register_new_seller(self.user_id, self.password)
        assert self.seller.create_store(self.store_id) == 200

        # 注册买家并下单
        self.buyer = register_new_buyer(f"buyer_{uuid.uuid1()}", "buyer_password")
        # 假设下单成功并返回订单ID
        self.order_id = self.buyer.place_order(self.store_id, book_id="book1", quantity=1)

    def test_ship_order_success(self):
        code, message = self.seller.ship_order(self.user_id, self.store_id, self.order_id)
        assert code == 200
        assert message == "Order shipped successfully"

    def test_ship_order_non_exist_order(self):
        non_exist_order_id = "non_exist_order"
        code, message = self.seller.ship_order(self.user_id, self.store_id, non_exist_order_id)
        assert code != 200
        assert "non_exist_order_id" in message 
```

### 收货功能
receive_order根据订单 ID 和用户 ID 查找订单。如果订单状态不是“shipped”（即未发货），则返回错误，提示订单未处于可收货状态。若订单状态为“shipped”，则更新订单状态为“received”，表示订单已收货。
```python
def receive_order(self, user_id: str, order_id: str) -> (int, str):
    try:
        # 查找订单
        order = self.conn["new_order"].find_one({"order_id": order_id, "user_id": user_id})
        if order is None:
            return error.error_invalid_order_id(order_id)
        
        # 检查订单状态是否为待收货
        if order.get("status") != "shipped":
            return 400, "Order not in a receivable state"

        # 更新订单状态为已收货
        self.conn["new_order"].update_one(
            {"order_id": order_id},
            {"$set": {"status": "received"}}
        )
    except PyMongoError as e:
        logging.error(f"Database error: {e}")
        return 528, f"{str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 530, f"{str(e)}"

    return 200, "Order received successfully"
```

#### 收货功能后端接口
用POST
```python
@bp_buyer.route("/receive_order", methods=["POST"])
def receive_order():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    b = Buyer()
    code, message = b.receive_order(user_id, order_id)
    return jsonify({"message": message}), code
```

#### 发货功能测试
先初始化用户、书店和订单，然后通过三个测试方法分别验证正常收货、订单未发货状态下的收货尝试，以及无效订单 ID 的处理情况。这确保了收货功能在不同状态下都能返回正确的响应码和消息。
```python
class TestReceiveOrder:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 初始化用户、书店、订单
        self.user_id = f"test_user_{str(uuid.uuid1())}"
        self.store_id = f"test_store_{str(uuid.uuid1())}"
        self.password = "test_password"
        self.order_id = "fake_order_id"

        # 注册卖家并创建书店
        self.seller = register_new_seller(self.user_id, self.password)
        assert self.seller.create_store(self.store_id) == 200

        # 注册买家并创建一个订单
        self.buyer = register_new_buyer(self.user_id, self.password)
        self.buyer.add_funds(1000)
        self.order_id = self.buyer.new_order(self.store_id, [{"id": "book1", "count": 1}])

    def test_receive_order_success(self):
        # 模拟订单发货状态
        self.seller.ship_order(self.store_id, self.order_id)

        # 买家收货
        code, message = self.buyer.receive_order(self.user_id, self.order_id)
        assert code == 200
        assert message == "Order received successfully"

    def test_receive_order_not_shipped(self):
        # 买家在订单未发货时尝试收货
        code, message = self.buyer.receive_order(self.user_id, self.order_id)
        assert code == 400
        assert message == "Order not in a receivable state"

    def test_receive_order_invalid_order_id(self):
        # 使用不存在的订单 ID
        invalid_order_id = "non_exist_order"
        code, message = self.buyer.receive_order(self.user_id, invalid_order_id)
        assert code != 200
        assert "invalid_order_id" in message
```


## 亮点

### git管理
本次项目中，我们用git来管理整个项目，小组成员共同完成开发，以下是我们的链接，https://github.com/ecnu-Sun/dbProject1.git








