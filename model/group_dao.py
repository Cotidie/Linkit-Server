from backend.database.file_system import Group
from backend.database.query import GroupQuery
from backend.database import DataBase
from backend.utils.exception import CustomException
from backend.config import MONGODB_COLLECTIONS as COLS

GROUP = COLS['group']

class GroupDAO():
    def __init__(self, db: DataBase):
        self.db = db
        self.group = db.get_collection(GROUP)

    def insert_groups(self, groups: list[Group]):
        query = [group.to_dict() for group in groups]
        self.group.insert_many(query)

        print("새로운 그룹 추가됨:", query)
        return True

    def create_group(self, member: str)->int:
        """
        새로운 그룹을 등록한다.
        @param member: 새로운 그룹의 최초 멤버
        @return: 생성된 gid
        """
        new_group = Group(members=[member])

        query = new_group.to_dict()
        self.group.insert_one(query)
        print("새로운 그룹 저장됨:", new_group.gid)
        return new_group.gid

    def get_groups(self, query: GroupQuery)->list[Group]:
        query = query.to_dict()
        filter = {'_id': 0}

        cursor = self.group.find(query, filter)
        groups = [Group.of(group) for group in list(cursor)]
        print(f"그룹을 읽었습니다: {groups}, 쿼리: {query}")
        return groups

    def update_group(self, query: GroupQuery, group: Group):
        query = query.to_dict()
        values = {'$set': group.to_dict()}

        result = self.group.update_one(query, values)
        if result.modified_count == 0:
            raise CustomException(code=5, is_global=True)

        return result.modified_count

    def delete_groups(self, gids: list[int]):
        query = {'gid': {'$in': gids}}
        self.group.delete_many(query)

        print(f"group 삭제함: {gids}")

    def clear_groups(self):
        """
        Group 콜렉션을 초기화한다.
            - 1번 그룹만 남긴다
        """
        root_group = self.get_groups(GroupQuery(gid=1))[0]
        self.group.delete_many({})
        self.insert_groups([root_group])