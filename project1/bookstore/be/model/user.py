import jwt
import time
import logging
import pymongo
from be.model import error

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    # For jwt>=2.0.0, encoded is a string
    return encoded


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms=["HS256"])
    return decoded


class User:
    token_lifetime: int = 3600  # 3600 seconds

    def __init__(self):
        # Connect to MongoDB
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['bookstore']
        self.user_col = self.db['user']
        # Ensure that user_id is unique
        self.user_col.create_index('user_id', unique=True)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False
        except jwt.exceptions.DecodeError as e:
            logging.error(str(e))
            return False
        return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            user_data = {
                'user_id': user_id,
                'password': password,
                'balance': 0,
                'token': token,
                'terminal': terminal
            }
            self.user_col.insert_one(user_data)
        except pymongo.errors.DuplicateKeyError:
            return error.error_exist_user_id(user_id)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        user = self.user_col.find_one({'user_id': user_id})
        if user is None:
            return error.error_authorization_fail()
        db_token = user['token']
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user = self.user_col.find_one({'user_id': user_id})
        if user is None:
            return error.error_authorization_fail()
        if password != user['password']:
            return error.error_authorization_fail()
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""
            token = jwt_encode(user_id, terminal)
            result = self.user_col.update_one(
                {'user_id': user_id},
                {'$set': {'token': token, 'terminal': terminal}}
            )
            if result.matched_count == 0:
                return error.error_authorization_fail() + ("",)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except Exception as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            result = self.user_col.update_one(
                {'user_id': user_id},
                {'$set': {'token': dummy_token, 'terminal': terminal}}
            )
            if result.matched_count == 0:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            result = self.user_col.delete_one({'user_id': user_id})
            if result.deleted_count == 0:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            result = self.user_col.update_one(
                {'user_id': user_id},
                {'$set': {'password': new_password, 'token': token, 'terminal': terminal}}
            )
            if result.matched_count == 0:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
