import jwt
from datetime import datetime
from bcrypt import gensalt, hashpw
from pymongo.errors import DuplicateKeyError
from google.oauth2 import id_token
from google.auth.transport import requests

from backend.model import Models
from backend.utils import Response, Category
from backend.utils.exception import CustomException

class UserService:
    def __init__(self, models: Models, config: dict):
        self.dao = models.user
        self.config = config
        self.category = Category.User

    def create_user(self, data: dict, res: Response):
        """ 유저의 회원가입 요청

        :param data: email, name, password, thumbnail로 구성된 dict
        :param res: Response 객체
        :return: (dict) 반환 메시지
        """
        if not data:
            res.status.set_code(1, is_global=True)
            return

        password = str(data.get('password')).encode(encoding='utf-8')
        # 비밀번호 암호화
        salt      = gensalt()
        hashed_pw = hashpw(password, salt)

        # DAO로 전달
        data['password'] = hashed_pw
        data['salt'] = salt

        try:
            self.dao.insert_user(data)
            self.dao.insert_credential(data)
        except DuplicateKeyError as e:
            res.status.set_code(1)

    def login_user(self, data: dict, res: Response):
        """ 유저의 로그인 요청

        :param data: email, password로 된 dictionary
        :return: (dict) 반환 메시지
        """
        # 유저가 요청한 정보
        email = data.get('email')
        password = data.get('password')
        # DB에 저장된 정보
        credential = self.dao.get_credential(email)
        if not credential:
            res.status.set_code(2)
            return

        # 패스워드 일치 확인
        if not self.match_password(password, credential):
            res.status.set_code(3)
            return

        return

    def match_password(self, user_pw: str, cred: dict):
        db_pw = cred.get('password')
        db_salt = cred.get('salt')

        hashed_pw = hashpw(user_pw.encode('utf-8'), db_salt)

        return db_pw == hashed_pw

    def google_login(self, token):
        """
        구글 계정토큰을 받아 계정 이메일을 반환한다.
        @param token: 구글 토큰
        @return: LinkIt 계정 이메일
        """
        client_id = self.config.get("GOOGLE_APP_CLIENT")
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        except ValueError as e:
            raise CustomException(4, is_global=False, message="토큰이 유효하지 않습니다.")

        user_data = {
            'email': idinfo['email'],
            'name': idinfo['name'],
            'thumbnail': idinfo['picture']
        }

        user = self.dao.get_user(idinfo['email'])
        if user is None:
            self.dao.insert_user(user_data)

        return user_data

    def create_access_token(self, email: str, paid: bool=False):
        payload = {
            'email': email,
            'paid': paid,
            'exp': datetime.now() + self.config['JWT_EXP']
        }
        token = jwt.encode(payload, key=self.config['JWT_KEY'])

        return token