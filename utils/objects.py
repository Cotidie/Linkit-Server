from typing import Union
from backend.utils.interfaces import IFile
from backend.utils.enums import FileType


class Ownership():
    def __init__(self, owner: str, gid: Union[int, None]):
        self.owner = owner
        self.gid = gid


class Link(IFile):
    def __init__(self):
        self.name = ""
        self.url = ""
        self.memo = ""
        self.img = ""
        self.tags = []

    def set_from(self, dict: dict):
        """ JSON 딕셔너리로부터 필드를 설정한다.
            - 필드는 name, url, tags, memo, img로 구성된다.
        """
        self.name = dict.get("name", "")
        self.url = dict.get("url")
        self.tags = dict.get("tags", [])
        self.memo = dict.get("memo", "")
        self.img = dict.get("img", "")

        return self

    # Override
    def get_type(self) -> FileType:
        return FileType.Link

    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'tags': self.tags,
            'memo': self.memo,
            'img': self.img
        }

    def __str__(self):
        return f"Link: {self.to_dict()}"


class Folder(IFile):
    def __init__(self, name="", img=""):
        self.name = name
        self.img = img

    def set_from(self, dict:dict):
        self.name = dict.get('name')
        self.img = dict.get('img')

        return self

    # Override
    def get_type(self) -> FileType:
        return FileType.Folder

    def to_dict(self):
        return {
            'name': self.name,
            'img': self.img
        }

    def __str__(self):
        return f"Folder: {self.to_dict()}"


class User():
    def __init__(self):
        pass