# CDMS.Xuan_ZHOU.2024Fall.DaSE

## 运行整体流程

在一次标准的测试流程中，首先搜索当前文件树下符合规则（以 test_ 开头、以 _test 结尾或位于 /fe/bench 目录）的测试文件。测试文件被调用后会触发前端逻辑，通过 /fe/access 向后端发送 HTTP 指令。后端接收指令后，通过 /be/view 中的函数解析 HTTP 参数并执行解析得到的指令，最终调用 /be/model 中的对应函数完成操作。

## 基础功能

### 卖家创建店铺
先判断卖家的用户ID或店铺是否存在
```python
if not self.user_id_exist(user_id):
    return error.error_non_exist_user_id(user_id)
if self.store_id_exist(store_id):
    return error.error_exist_store_id(store_id)
```

如果用户ID存在且店铺不存在，则把这两者插入到user_store里
```python
user_store_doc = {
    'store_id': store_id,
    'user_id': user_id,
}
self.conn['user_store'].insert_one(user_store_doc)
```

这个文件对应test_create_store.py文件，两个测试用例：test_ok和test_error_exist_store_id。test_ok会注册一个新用户并以该用户创建一个店铺；test_error_exist_store_id创建一次同一个店铺，用于测试创建已经存在的店铺时是否成功报错。



### 卖家在店铺中添加书籍信息
要确保userid，storeid，bookid都存在
```python
if not self.user_id_exist(user_id):
    return error.error_non_exist_user_id(user_id)
if not self.store_id_exist(store_id):
    return error.error_non_exist_store_id(store_id)
if self.book_id_exist(store_id, book_id):
    return error.error_exist_book_id(book_id)
```

插入到store里
```python
book_doc = {
    'store_id': store_id,
    'book_id': book_id,
    'book_info': book_json_str,
    'stock_level': stock_level,
}
self.conn['store'].insert_one(book_doc)
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
self.conn['store'].update_one(
    {'store_id': store_id, 'book_id': book_id},
    {'$inc': {'stock_level': add_stock_level}},
)
```

卖家增加库存函数对应test_add_stock_level文件，test_ok测试接口基本功能，test_error_non_exist_store_id、test_error_exist_book_id和test_error_non_exist_user_id分别用于测试店铺、书籍、卖家不存在时系统是否报错。





## 亮点

### git管理
本次项目中，我们用git来管理整个项目，小组成员共同完成开发，以下是我们的链接，https://github.com/ecnu-Sun/dbProject1.git








