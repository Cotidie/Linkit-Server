# 스탠다드 라이브러리
# 서드파티 라이브러리
from flask  import Blueprint, request, jsonify, g
import pprint
from backend.utils import Response, Category
from backend.service import Services
from backend.utils.decorators import json_required
from backend.utils.exception import CustomException
from backend.utils.communicate import debug_request

def create_user_view(services: Services):
    user_view = Blueprint('user', __name__)

    user_service = services.user

    @user_view.route('/sign-up', methods=['POST'])
    def sign_up():
        """ 새로운 유저 회원가입 요청

        - 이메일이 중복된 유저는 회원가입하지 못한다.
        """
        # 응답 객체
        result = Response(cat=Category.User)

        # 데이터 받기
        new_user = request.get_json()
        user_service.create_user(new_user, result)

        return jsonify(result), result.get_http()


    # TODO: Exception 클래스 정의하여 redict message 처리하기
    @user_view.route('/login', methods=['POST'])
    def login():
        """로그인 API. 로그인에 성공하면 access token을 발급한다.

        - 들어오는 JSON은 'email', 'password'로 구성된다.
        - pyJWT로 access token을 발급한다.
        """
        res = Response(cat=Category.User)

        # 데이터 받기
        credential  = request.get_json()
        user_service.login_user(credential, Response)

        if not res.status.success:
            return jsonify(res), res.get_http()

        # 인증토큰 발급
        access_token = user_service.create_access_token(credential['email'])

        # 결과 반환
        res.data['access_token'] = access_token
        return jsonify(res), res.get_http()

    @user_view.route('/login/google', methods=['POST'])
    @json_required
    def login_google():
        """
        구글 OAuth로 회원가입하거나 로그인한다.
            - 등록되지 않은 이메일은 회원가입한다.
            - 등록된 이메일은 바로 로그인한다.
        @return:
        """
        print("--------------------------/login/google--------------------------")
        res = Response(cat=Category.User)
        data = g.get('json')
        id_token = data['token']
        if not id_token:
            res.status.set_code(code=2, is_global=True); print(res)
            return jsonify(res), res.get_http()

        # 신규가입 또는 로그인
        try:
            user = user_service.google_login(id_token)
        except CustomException as e:
            res.status.set_code(code=e.code, is_global=e.is_global)
            return jsonify(res), res.get_http()

        # 유저정보
        email = user['email']; print(email)
        name = user['name']; print(name)

        # 액세스 토큰 발급
        access_token = user_service.create_access_token(user['email'])

        # 결과 반환
        res.data['access_token'] = access_token
        res.data['email'] = email
        res.data['name'] = name

        return jsonify(res), res.get_http()

    return user_view
