from .user_dao import UserDAO
from .link_dao import LinkDAO
from .group_dao import GroupDAO
from backend.database import DataBase


# 단순히 변수를 담기 위한 클래스
class Models:
    def __init__(self, db: DataBase):
        self.user = UserDAO(db)
        self.link = LinkDAO(db)
        self.group = GroupDAO(db)