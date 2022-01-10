# 데코레이터 이용 라이브러리
from functools import wraps
from flask import request, jsonify, current_app as app, g
import jwt
# 커스텀
from backend.utils import Response


def login_required(f):
    """
    인증토큰을 요구하는 데코레이터. 그 과정에서 g.email에 유저 이메일을 저장한다.
    :param f: inner function
    """

    @wraps(f)
    def decorated_func(*args, **kwargs):
        res = Response()

        access_token = request.headers.get('Authorization')
        if not access_token:
            # 토큰이 없는 경우
            res.status.set_code(3)
            return jsonify(res), res.get_http()

        # 토큰 복호화
        try:
            payload = jwt.decode(access_token,
                        app.config.get('JWT_KEY'),'HS256')
        except jwt.InvalidTokenError:
            res.status.set_code(4)
            return jsonify(res), res.get_http()

        g.email = payload['email']

        return f(*args, **kwargs)

    return decorated_func


def json_required(f):
    """
    JSON 데이터를 요구하는 데코레이터
    """
    @wraps(f)
    def decorated_func(*args, **kwargs):
        res = Response()
        data = request.get_json()
        if not data:
            res.status.set_code(1)
            return jsonify(res), res.get_http()

        g.json = data

        return f(*args, **kwargs)
    return decorated_func
