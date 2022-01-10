from abc import abstractmethod
from backend.utils.enums import FileType

class IFile():
    @abstractmethod
    def get_type(self) -> FileType:
        pass