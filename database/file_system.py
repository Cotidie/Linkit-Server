from uuid import uuid4
from abc import abstractmethod
from typing import Union

from backend.utils.objects import Link, Folder, Ownership
from backend.utils.enums import FileType


class Snode:
    # 필드명과 타입
    FIELDS = {
        'snode': int,
        'type': FileType,
        'owner': str,
        'gid': int,
        'block': int,
    }

    def __init__(self, type: FileType, ownership: Ownership, snode: int = None, block: int = None):
        self.snode = create_unique_id() if not snode else snode
        self.type = type
        self.ownership = ownership
        self.block = create_unique_id() if not block else block

    def set_ownership(self, ownership: Ownership):
        self.ownership = ownership
        return self

    def _set_from_dict(self, dict: dict):
        snode = dict['snode']
        type = dict['type']
        owner = dict['owner']
        group = dict['gid']
        block = dict['block']

        self.snode = snode
        self.type = FileType(type)
        self.ownership = Ownership(owner, group)
        self.block = block

        return self

    def _set_from_folder(self, folder: Folder):
        pass

    def to_dict(self):
        return {
            'snode': self.snode,
            'type': self.type.value,
            'owner': self.ownership.owner,
            'gid': self.ownership.gid,
            'block': self.block,
        }

    @staticmethod
    def of(obj):
        """ snode를 표현하는 객체들로부터 Snode를 만든다.
            - DB 쿼리 결과를 Snode 객체로 만든다.
        """
        # 더미노드, 타입과 Ownership은 다른 객체로부터 설정된다.
        if not obj:
            return None

        new_node = Snode(snode=1, type=FileType.Folder,
                         ownership=Ownership("", None))
        if isinstance(obj, dict):
            new_node._set_from_dict(obj)
        if isinstance(obj, Folder):
            new_node._set_from_folder(obj)

        return new_node

    def __str__(self):
        return f"Snode: {self.to_dict()}"

    def __repr__(self):
        return str(self.snode)


class Block:
    def __init__(self, snode: int, block=1, name=""):
        """
        Block은 사용자에게 표시할 메타 정보를 담는다.
        """
        self.block = block
        self.snode = snode
        self.name = name
        self.type = FileType.Folder

    def of(self, obj):
        """
            대응하는 파일 형식에 따라 LinkBlock, FolderBlock을 반환한다..
        """
        casted = None
        if isinstance(obj, Link):
            casted = LinkBlock(self.snode, self.block)
        elif isinstance(obj, Folder):
            casted = FolderBlock(self.snode, self.block)
        elif isinstance(obj, dict):
            if 'url' in obj.keys():
                casted = LinkBlock(self.snode, self.block)
            else:
                casted = FolderBlock(self.snode, self.block)
        casted.set_from(obj)

        return casted

    def set_from_dict(self, obj: dict):
        for key in obj.keys():
            setattr(self, key, obj[key])

        return self

    @abstractmethod
    def set_from(self, obj):
        pass

    @abstractmethod
    def to_dict(self):
        return {
            'snode': self.snode,
            'block': self.block,
            'name': self.name,
        }

    def to_content_dict(self):
        return {'name': self.name}

    def __str__(self):
        return f"Block: {self.to_dict()}"

    def __repr__(self):
        return str(self)


class FolderBlock(Block):
    def __init__(self, snode: int, block=1, name="", img=""):
        super().__init__(snode, block)
        self.name = name
        self.img = img
        self.type = FileType.Folder

    def set_from(self, obj: Union[Folder, dict]):
        if isinstance(obj, dict):
            return self.set_from_dict(obj)

        self.name = obj.name
        self.img = obj.img

        return self

    def to_content_dict(self):
        return {
            'name': self.name,
            'img': self.img
        }

    # Override
    def to_dict(self):
        origin = super().to_dict()
        origin.update(self.to_content_dict())
        return origin

    def __str__(self):
        return f"FolderBlock: {self.to_dict()}"


class LinkBlock(Block):
    def __init__(self, snode: int, block=1):
        super().__init__(snode, block)
        self.url = ""
        self.memo = ""
        self.img = ""
        self.tags = []
        self.type = FileType.Link

    def set_from(self, obj: Link):
        if isinstance(obj, dict):
            return self.set_from_dict(obj)

        self.name = None
        self.url = obj.url
        self.memo = obj.memo
        self.img = obj.img
        self.tags = obj.tags

        return self

    def to_content_dict(self):
        return {
            'url': self.url,
            'memo': self.memo,
            'img': self.img,
            'tags': self.tags
        }

    # Override
    def to_dict(self):
        origin = super().to_dict()
        origin.update(self.to_content_dict())
        return origin


class Group:
    def __init__(self, gid: int=None, members=None):
        self.gid = create_unique_id() if not gid else gid
        self.members = [] if not members else members

    def add_member(self, email: str):
        if self.members.count(email) > 0:
            return

        self.members.append(email)

    def to_dict(self):
        return {
            'gid': self.gid,
            'members': self.members
        }

    @staticmethod
    def of(dict: dict):
        if not dict:
            return None

        group = Group()
        for key in dict.keys():
            setattr(group, key, dict[key])

        return group

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.gid)

def create_unique_id():
    return uuid4().int & (1<<63)-1