import ssl

from pymongo import MongoClient, collection
from pymongo.errors import CollectionInvalid
from backend.config import MONGODB_COLLECTIONS as COLS

CONFIG = COLS['config']

class DataBase(MongoClient):
    """MongoDB 설정해주는 클래스
    Args:
            host (str, optional): DB 호스트 명
            db (str, optional): DB 이름
    """
    def __init__(self, host: str, db: str):
        #super().__init__(host, ssl_cert_reqs=ssl.CERT_NONE)
        super().__init__(host)

        self.db = self[db]
        self.host = host         # DB 호스트 명
        self.cols = self.db.list_collection_names()

    def get_collection(self, name) -> collection.Collection:
        """데이터베이스에서 원하는 pymongo collection을 가져온다
        Args:
                name (str): COLLECTIONS 배열안에 정의된 이름만 가능
        Raises:
                pymongo.erros.CollectionInvalid: 잘못된 Collection 이름
        """
        name = name.lower()

        # Wrapper 클래스가 있으면 Wrapper로 반환
        if name in self.cols:
            return self.db[name]
        else:
            raise CollectionInvalid("콜렉션{" + name + "} 이름이 잘못되었습니다")

    def get_config(self, target: str=None):
        """ DB에 저장된 설정값을 가져온다.

        :param target: 설정값 필드
        :return: 해당하는 필드값
        """
        collection = self.get_collection(CONFIG)

        my_query = {'id': 'config'}
        my_result = {target: True}

        result = collection.find_one(my_query, my_result)
        if not result:
            return None

        return result[target]