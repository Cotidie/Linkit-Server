import sys      # 강제종료
import os       # 환경변수 읽기
from datetime import timedelta

from os.path import isfile          # 파일 존재 확인

"""
 from_pyfile()로 읽어들일 Flask config 파일
  * 변수명은 반드시 대문자로 설정해야 한다.
  * 공통 접두사는 Flask에서 namespace로 활용한다.
"""

# MongoDB 주소 얻어오기
if not isfile("db_host.0"):
    MONGODB_HOST = os.environ.get('DB_TOKEN')
    if not MONGODB_HOST:
        sys.exit("DB 토큰을 찾을 수 없습니다. 관리자에게 문의하세요.")
else:
    with open("db_host.0") as file:
        MONGODB_HOST = file.read()

MONGODB_DB = 'LinkManage'
MONGODB_COLLECTIONS = {
    'config': 'config',
    'user': 'user',
    'credential': 'credential',
    'snode': 'snode',
    'group': 'group',
    'block': 'block',
}

# JWT Setting
JWT_EXP = timedelta(days=365)

# OAuth Setting
GOOGLE_APP_CLIENT = '1051223861817-83pu7u0ubjetbj763rai3d65iqf5898g.apps.googleusercontent.com'

# Custom Settings
ADMINS = [
    'daily142857@gmail.com'
]