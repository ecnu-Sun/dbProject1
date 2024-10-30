import random
import base64
from pymongo import MongoClient

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [str]

    def __init__(self):
        self.tags = []
        self.pictures = []

class BookDB:
    # 初始化连接到 MongoDB
    def __init__(self, large: bool = False):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["bookstore"]
        self.collection = self.db["books"]  # 使用 book 集合来存储和查询图书信息

    # 获取图书数量
    def get_book_count(self):
        # 计算 book 集合中所有图书的数量
        return self.collection.count_documents({})

    # 获取图书信息，start: 初始偏移量, size: 数量
    def get_book_info(self, start, size) -> [Book]:
        books = []
        # 在 book 集合中分页查询图书
        cursor = self.collection.find({}, skip=start, limit=size)

        for document in cursor:
            book = Book()

            # 将查询结果映射到 Book 对象
            book.id = document.get("id")
            book.title = document.get("title")
            book.author = document.get("author")
            book.publisher = document.get("publisher")
            book.original_title = document.get("original_title")
            book.translator = document.get("translator")
            book.pub_year = document.get("pub_year")
            book.pages = document.get("pages")
            book.price = document.get("price")
            book.currency_unit = document.get("currency_unit")
            book.binding = document.get("binding")
            book.isbn = document.get("isbn")
            book.author_intro = document.get("author_intro")
            book.book_intro = document.get("book_intro")
            book.content = document.get("content")

            # 处理标签
            tags = document.get("tags", "")
            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)

            # 处理图片
            picture = document.get("picture")
            for i in range(random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)

            books.append(book)

        return books
