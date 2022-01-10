# 서드파티 라이브러리
from flask import Blueprint, jsonify, g, request
from backend.utils import Response, Category
from backend.utils.decorators import login_required, json_required
from backend.utils.exception import CustomException
from backend.utils.communicate import debug_request
from backend.service import Services


def create_link_view(services: Services):
    view = Blueprint('link', __name__)
    service_link = services.link


    @view.route('/insert', methods=['POST'])
    @login_required
    @json_required
    def insert():
        """ 사용자의 폴더/링크들을 공유 상태로 만든다.

        """
        result = Response(cat=Category.Link)
        raw_json = g.get('json')

        meta = raw_json['meta']
        data = raw_json['data']
        if not meta or not data:
            result.status.set_code(2, True)
            return jsonify(result), result.get_http()

        print('--------------------/insert--------------------')
        print('meta:', meta)
        print('data:', data)

        # 공유폴더/파일 등록하기
        try:
            gid, snodes = service_link.register_files(meta, data)
        except CustomException as e:
            print(e)
            result.status.set_code(e.code, e.is_global)
            return jsonify(result), result.get_http()

        result.data = {
            'gid': gid,
            'snodes': snodes,
        }

        return jsonify(result), result.get_http()

    @view.route('/read', methods=['POST'])
    @login_required
    @json_required
    def read():
        """
        snode로부터 폴더/링크 정보를 읽는다.
        """
        print("--------------------------/link/read--------------------------")
        debug_request(request)
        response = Response(cat=Category.Link)
        data = g.get('json');                       print(f"data: {data}")

        node_num = data.get('snode', None)
        email = data.get('email', None)
        if node_num is None and email is None:
            response.status.set_code(2, is_global=True)
            return jsonify(response), response.get_http()

        try:
            if node_num:
                result = service_link.read_files(node_num)
            elif email:
                result = service_link.read_by_email(email)
            response.data = result
        except CustomException as e:
            print(e)
            response.status.set_code(e.code, e.is_global)
            return jsonify(response), response.get_http()

        print("--------------------------/link/read--------------------------")
        return jsonify(response), response.get_http()

    @view.route('/delete', methods=['POST'])
    @login_required
    @json_required
    def delete():
        """
            TODO: 삭제 권한(Owner) 검사
        """
        print("--------------------------/link/delete--------------------------")
        response = Response(cat=Category.Link)
        data = g.get('json')
        node_nums = data.get('snodes', None);                   print(f"요청 노드: {node_nums}")
        if node_nums is None:
            response.status.set_code(2)
            return jsonify(response), response.get_http()

        try:
            service_link.delete_files(node_nums)
        except CustomException as e:
            print(e)
            response.status.set_code(e.code, e.is_global)
            return jsonify(response), response.get_http()

        print("--------------------------/link/delete--------------------------")
        return jsonify(response), response.get_http()

    @view.route('move', methods=['POST'])
    @login_required
    @json_required
    def move():
        """
        폴더나 파일의 위치를 다른 폴더로 이동한다
         - json: snodes, from, to로 구성
         - 대상 파일들은 이동 후 폴더의 gid로 변경된다.
        """
        print("--------------------------/link/move--------------------------")
        res = Response(cat=Category.Link)

        data = g.get('json');                       print(f"요청 데이터: {data}")
        before = data.get('from')
        after = data.get('to')
        snodes = data.get('snodes')
        if not before or not after or not snodes:
            res.status.set_code(2, is_global=True); print(res)
            return jsonify(res), res.get_http()

        try:
            service_link.move_files(snodes, before, after)
        except CustomException as e:
            print(e)
            res.status.set_code(e.code, is_global=e.is_global)
            return jsonify(res), res.get_http()

        print("--------------------------/link/move--------------------------")
        return jsonify(res), res.get_http()

    @view.route('/update', methods=['POST'])
    @login_required
    @json_required
    def update():
        print("--------------------------/link/update--------------------------")
        res = Response(cat=Category.Link)
        data = g.get('json');               print(f"요청 데이터: {data}")
        snode = data.get('snode')
        update = data.get('update')
        if not snode or not update:
            res.status.set_code(2, is_global=True); print(res)
            return jsonify(res), res.get_http()

        try:
            service_link.update_file(snode, update)
        except CustomException as e:
            res.status.set_code(e.code, e.is_global); print(res)
            return jsonify(res), res.get_http()

        print("--------------------------/link/update--------------------------")
        return jsonify(res), res.get_http()

    return view