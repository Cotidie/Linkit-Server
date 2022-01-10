# Standard 라이브러리
import json
from enum import Enum
from datetime import datetime
from typing import Any

# Third Party 라이브러리
from bson     import ObjectId
from backend.utils.response import Response


class DataEncoder(json.JSONEncoder):
    """ Flask의 json 인코더의 변환 타입을 확장
    JSON 통신에 필요한 타입이 생길 때마다 추가해준다.
    """
    def default(self, o: Any) -> Any:
        # bson.ObjectID(MongoDB id) => string
        if isinstance(o, ObjectId):
            return str(o)
        # datetime => isoformat
        if isinstance(o, datetime):
            return o.isoformat()
        # Response => dict
        if isinstance(o, Response):
            return o.to_dict()
        # Enum => Enum.value
        if isinstance(o, Enum):
            return o.value

        # 명시되지 않은 타입은 기본 기능 사용
        return super().default(o)
    