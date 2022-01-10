from enum import Enum

class Category(Enum):
    Global  = 0
    User    = 100
    Link    = 200
    Group   = 300

class FileType(Enum):
    Link = 1
    Folder = 2