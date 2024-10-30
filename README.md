# 第一次大作业：书店
## 小组成员
- **孙钊琳** 分工：用户权限接口，搜索图书
- **庄欣熠** 10225501451 分工：卖家用户接口，发货收货
- **刘江涛** 10225501445 分工：买家用户接口，订单状态

## 文档数据库设计
对原来sqlite数据库schema稍作修改后，我们使用三个文档集合: *user* , *store*, *new_order*。

### 文档示例

_**user:**_
```python
{
  "_id": ObjectId("..."),  // MongoDB 自动生成的唯一标识符
  "user_id": "unique_user_id",  // 用户唯一 ID，索引字段
  "password": "hashed_password",
  "balance": 1000,  // 用户余额
  "token": "jwt_token",
  "terminal": "user_terminal_info"
}

```
**_store:_**
```python
{
  "_id": ObjectId("..."),
  "store_id": "unique_store_id",  // 书店唯一 ID，索引字段
  "user_id": "unique_user_id",  // 店主的用户 ID
  "books": [
    {
      "book_id": "unique_book_id",  // 每本书的唯一 ID，嵌套索引字段
      "book_info": {//与access/book.py中的Book类定义相同
        "title": "Book Title",
        "author": "Author Name",
        "price": 50,
        // 其他书籍相关信息
      },
      "stock_level": 100  // 库存量
    },
    // 更多书籍...
  ]
}
```

**_new_order:_**
```python
{
  "_id": ObjectId("..."),
  "order_id": "unique_order_id",  // 订单唯一 ID，索引字段
  "user_id": "unique_user_id",  // 下单的用户 ID
  "store_id": "unique_store_id",  // 书店的 ID
  "items": [
    {
      "book_id": "unique_book_id",
      "count": 2,
      "price": 50  // 每本书的单价
    }
    // 更多书籍条目...
  ],
  "total_price": 100,  // 订单总价
  "status": "pending",  // 订单状态，pending,completed,cancelled
}
```

### 文档索引

**_user:_**
- user_id 

**_store_**
- store_id 
- (store_id , books.book_id) 复合索引

_**new_order**_
- order_id
- (order_id , items.book_id) 符合索引 

## 运行整体流程

在一次标准的测试流程中，首先搜索当前文件树下符合规则（以 test_ 开头、以 _test 结尾或位于 /fe/bench 目录）的测试文件。测试文件被调用后会触发前端逻辑，通过 /fe/access 向后端发送 HTTP 请求。后端接收请求后，通过 /be/view 中的函数解析 HTTP 参数并执行解析得到的指令，最终调用 /be/model 中的对应函数完成操作,然后将结果返回给测试文件，由测试文件判断正误。

## 基础功能
### 适配mongodb

为了适配mongodb数据库，我们需要把 *fe\data\bood.db* 数据库里的数据转移到本地运行的mongodb数据库中。我们使用 *bookstore \ transData.py* 来进行数据迁移，在本地数据库创建了 books 集合，用于存储数据。详见 *bookstore \ transData.py*

然后，在后端服务器启动时，我们需要创建如上述 **schema** 定义的三个集合： *user* , *store* , *new_order*。这三个集合及其索引的创建在 *be \ model \ store.py* 中。之后的基础功能实现中，都在这里创建的三个mongodb文档集合中操纵数据。由于 *be \ model \ db_conn.py* 中的类掌管与数据库的交互，因此也需要将它修改为适配mongodb的语法。详见 *store.py* 与 *db_conn.py* 注释。

除此之外，注意到fe \ access \ book.py 中需要书籍数据来进行测试，因此我们为这个模块连接上 books 文档集合，详见 *fe \ access \ book.py*

完成了这些,剩下要做的就是对 *model* 文件夹中的 *user.py、buyer.py、seller.py* 进行相应改造，以适配现在的mongodb数据库。


### 用户权限接口
--written by 孙钊琳










### 买家接口
--written by 刘江涛

接口在 be \ view \ buyer.py 中实现，用于接收测试线程发来的http请求，并解析参数，然后传递给后端的支持函数（存放在be \ model \ buyer.py中）。

后端逻辑在be \ model \ buyer.py中实现。修改了 _new_order()_ , _payment()_ , _add_funds()_ 函数，以适配 mongodb 数据库，主要逻辑与原来大致相同，详见代码注释。

沿用原本的测试函数。

### 卖家接口 
--written by庄欣熠
#### 卖家创建店铺
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



#### 卖家在店铺中添加书籍信息
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

#### 卖家增加库存
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
### 发货、收货功能
--written by 庄欣熠

**发货**

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

**发货功能后端接口**

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
**发货功能测试**

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

**收货**

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

**收货功能后端接口**

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

**发货功能测试**

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

### 图书搜索
--written by 孙钊琳















### 订单状态
--written by 刘江涛

**增加字段**

为了实现订单查询和订单取消，我在修改了原来的new_order文档集合的管理方式，当订单支付成功后，**不删除订单**，而是**修改订单状态**

我定义了三种状态：pending , completed , cancelled这些状态存储在每个 new_order 文档的 “status” 字段中。

在 *buyer.py* 的 *new_order()* 函数中， 一个新的订单被创建时，它的订单状态被设定为 pending：

```python
order={
    "order_id": uid,
    "user_id": user_id,
    "store_id": store_id,
    "items": items,
    "total_price": total_price,
    "status": "pending",  # 订单状态为 `pending`
}
```
在*buyer.py* 的 *payment()* 函数中，一个订单被付款时，首先要判断它的订单状态必须为pending:
```python
if order.get("status") != "pending":
    return error.error_invalid_order_status(order_id)
```
然后付款成功时，修改订单状态为 completed:
```python
self.conn["new_order"].update_one(
    {"order_id": order_id},
    {"$set": {"status": "completed"}}
)
```

**订单查询**

直接在利用user_id,在new_order文档集合中搜索对应用户的订单，并返回一个历史订单表：
```python
def get_user_orders(self, user_id: str):
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + ([],)
        
            orders = self.conn["new_order"].find({"user_id": user_id})
            
            
            orders_list = []
            for order in orders:
                order["_id"] = str(order["_id"])  
                orders_list.append(order)
            
            return 200, "ok", orders_list
        except PyMongoError as e:
            logging.error(f"Database error in get_user_orders: {e}")
            return 528, f"{str(e)}", []
```
详见 *be \ model \ buyer.py get_user_orders()* 函数

为了对这个功能进行测试，我需要在*fe \ access \ buyer.py* 中添加对应的发送请求的函数，详见 *fe \ access \ buyer.py order_history()* 函数

还需要在 *be \ view \ buyer.py* 中添加对应的接收请求的函数，详见 *be \ view \ buyer.py order_history()* 函数

关于测试函数，测试了 "没有历史记录"、"有历史记录"、"用户不存在" 这三种情况。详见 *fe \ test \ test_order_history.py* 。

**取消订单**

先检查订单状态，必须为 *pending* 才能取消。然后更新订单状态为 *cancelled*。最后为书店恢复库存。
```python
def cancel_order(self, user_id: str, order_id: str):
        try:
            # 查询订单信息
            order = self.conn["new_order"].find_one({"order_id": order_id, "user_id": user_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            # 检查订单状态
            if order["status"] != "pending":
                return 400, "Order cannot be cancelled"

            # 更新订单状态为 `cancelled`
            self.conn["new_order"].update_one({"order_id": order_id}, {"$set": {"status": "cancelled"}})
            
            # 恢复库存
            for item in order["items"]:
                self.conn["store"].update_one(
                    {"store_id": order["store_id"], "books.book_id": item["book_id"]},
                    {"$inc": {"books.$.stock_level": item["count"]}}
                )
        except PyMongoError as e:
            logging.error(f"Database error in cancel_order: {e}")
            return 528, f"{str(e)}"
        except Exception as e:
            logging.error(f"Unexpected error in cancel_order: {e}")
            return 530, f"{str(e)}"

        return 200, "ok"

```
同样地，我在 *fe \ access \ buyer.py* 中添加对应的发送请求的函数，详见 *fe \ access \ buyer.py cancel_order()* 函数

还在 *be \ view \ buyer.py* 中添加了对应的接收请求的函数，详见 *be \ view \ buyer.py cancel_order()* 函数

关于测试函数，测试了 "取消不存在订单"、"无效用户id"、"正常情况"、"订单状态不为pending"的情况，详见 *fe \ test \ test_cancel_order.py*

## 测试结果
**覆盖率**：

![Alt text](report_image\覆盖率.png "Optional Title")

总体覆盖率为90%

**通过情况**

![Alt text](report_image\通过情况.png "Optional Title")

测试程序全部通过
## git管理
本次项目中，我们用git来管理整个项目，小组成员共同完成开发，以下是我们的链接，https://github.com/ecnu-Sun/dbProject1.git








