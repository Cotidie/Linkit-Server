from typing import Union
from backend.utils.enums import Category, FileType
from backend.utils.exception import CustomException
from backend.model import Models
from backend.database.file_system import Group
from backend.database.query import GroupQuery

class GroupService():
    def __init__(self, models: Models, config):
        self.model_group = models.group
        self.config = config
        self.category = Category.Group

    def validate_gid(self, gid: int) -> Group:
        """
        gid가 유효한지 검사한다.
        @return: Group, 없으면 None
        """
        query = GroupQuery(gid=gid)
        group = self.model_group.get_groups(query)
        if not group:
            raise CustomException(code=1, is_global=False)

        return group[0]

    def validate_email(self, email: str):
        return True

    def add_users(self, gid: int, emails: list[str]):
        group = self.validate_gid(gid)
        ## self.validate_email(email) 존재하는 이메일인지 검사해야 한다.

        for email in emails:
            group.add_member(email)

        query = GroupQuery(gid=group.gid)
        self.model_group.update_group(query, group)