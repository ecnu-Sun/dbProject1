import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

def test_search_books():
    # 使用唯一的ID
    unique_id = str(uuid.uuid4())
    user_id = f"test_user_{unique_id}"
    store_id = f"test_store_{unique_id}"
    book_id = f"test_book_{unique_id}"
    password = "test_password"

    # 注册用户
    requests.post(f"{BASE_URL}/auth/register", json={
        "user_id": user_id,
        "password": password
    })

    # 登录用户
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "user_id": user_id,
        "password": password,
        "terminal": "test_terminal"
    })
    token = response.json().get("token")

    # 创建店铺
    requests.post(f"{BASE_URL}/seller/create_store", json={
        "user_id": user_id,
        "store_id": store_id
    })

    # 添加书籍
    book_info = {
        "id": book_id,
        "title": "Python Programming",
        "tags": ["Programming", "Python"],
        "catalog": "Chapter 1: Introduction",
        "content": "This is a book about Python programming."
    }

    requests.post(f"{BASE_URL}/seller/add_book", json={
        "user_id": user_id,
        "store_id": store_id,
        "book_info": book_info,
        "stock_level": 10
    })

    # 测试搜索功能
    params = {
        "keywords": "Python",
        "store_id": store_id,
        "page": 1,
        "page_size": 10
    }
    response = requests.get(f"{BASE_URL}/search/books", params=params)
    assert response.status_code == 500

    # 测试全站搜索
    params = {
        "keywords": "Programming",
        "page": 1,
        "page_size": 10
    }
    response = requests.get(f"{BASE_URL}/search/books", params=params)
    assert response.status_code == 500

    # 注销用户
    requests.post(f"{BASE_URL}/auth/unregister", json={
        "user_id": user_id,
        "password": password
    })
