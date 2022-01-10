from .user_service import UserService
from .link_service import LinkService
from .group_service import GroupService
from backend.model import Models

# 단순히 변수를 담기 위한 클래스
class Services:
    def __init__(self, models: Models, config: dict):
        self.user = UserService(models, config)
        self.link = LinkService(models, config)
        self.group = GroupService(models, config)
