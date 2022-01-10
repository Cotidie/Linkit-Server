# Standard
from datetime import datetime
# Third-Party
from pytz import timezone
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
# Custom
from backend.config import MONGODB_COLLECTIONS as COLS
from backend.database import DataBase

USER        = COLS['user']
CREDENTIAL  = COLS['credential']


class UserDAO:
    def __init__(self, db: DataBase):
        self.db = db

    def get_user(self, email: str):
        """ DB에 저장된 유저 정보를 가져온다.

        :param email: 찾을 유저 이메일
        :return: dictionary. 없으면 None
        """
        collection = self.db.get_collection(USER)

        my_query = {'email': email}

        return collection.find_one(my_query)

    def insert_user(self, data: dict):
        """ 새로운 유저를 추가한다.

        :param data: email, name, thumbnail, password, salt로 구성된 딕셔너리
        :param res: Response 객체
        :return: None
        """
        email       = data.get('email')
        name        = data.get('name')
        thumbnail   = data.get('thumbnail', None)
        KST_now     = datetime.now(tz=timezone('Asia/Seoul'))

        new_user = {
            'email': email,
            'name': name,
            'thumbnail': thumbnail,
            'created': KST_now,
            'last_login': KST_now
        }

        col_user = self.db.get_collection(USER)

        # 추가 시도. 각 컬렉션은 email 필드에 Unique 설정되어 있다.
        try:
            col_user.insert_one(new_user)
        except DuplicateKeyError as e:
            raise e

    def insert_credential(self, data: dict):
        col_cred = self.db.get_collection(CREDENTIAL)

        email = data.get('email')
        hashed_pw   = data.get('password')
        salt        = data.get('salt')

        new_cred = {
            'email': email,
            'password': hashed_pw,
            'salt': salt
        }

        # 추가 시도. 각 컬렉션은 email 필드에 Unique 설정되어 있다.
        try:
            col_cred.insert_one(new_cred)
        except DuplicateKeyError as e:
            raise e



    def get_credential(self, email: str):
        """ DB에 저장된 유저의 보안 정보를 가져온다.

        :param email: 찾을 유저 이메일
        :return: dictionary, 없으면 None
        """
        collection = self.db.get_collection(CREDENTIAL)

        my_query = {'email': email}

        return collection.find_one(my_query)
