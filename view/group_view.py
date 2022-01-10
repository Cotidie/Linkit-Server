from flask import Blueprint, jsonify, g, request
from backend.utils.decorators import login_required, json_required
from backend.utils.response import Response
from backend.utils.enums import Category
from backend.utils.exception import CustomException
from backend.service import Services

def create_group_view(services: Services):
    view = Blueprint('group', __name__)
    service_group = services.group

    @view.route('/add', methods=['POST'])
    @login_required
    @json_required
    def add():
        """
        해당하는 gid에 새로운 유저를 추가한다.
         * 요청인자: gid, email
         - 요청자 토큰의 이메일은 대상 gid에 속해 있어야 한다.
         - 유효한 gid, 이메일 목록이어야 한다.
        """
        res = Response(cat=Category.Group)

        data = g.get('json')
        gid = data.get('gid')
        email = data.get('email')
        if (not gid or not email) or\
            not isinstance(email, list):
            res.status.set_code(2, is_global=True)
            return jsonify(res), res.get_http()

        try:
            service_group.add_users(gid, email)
        except CustomException as e:
            res.status.set_code(code=e.code, is_global=e.is_global)
            return jsonify(res), res.get_http()

        return jsonify(res), res.get_http()

    return view