from flask import Blueprint, jsonify, request
from backend.utils import Response
from backend.utils.communicate import debug_request
from backend.service import Services
from backend.utils.decorators import login_required


def create_developer_view(services: Services):
    developer_view = Blueprint('developer', __name__)
    link_service = services.link

    @developer_view.route('/test', methods=['POST', 'GET'])
    def test():
        r = Response()
        data = request.get_json()
        debug_request(request)
        print(data)

        return jsonify(r), r.get_http()

    @developer_view.route('/cleardb', methods=['POST'])
    @login_required
    def clear_database():
        """
        - 블럭은 루트폴더의 현재폴더만 남긴다.
        """
        print('--------------------/cleardb--------------------')
        res = Response()
        link_service.clear_database()

        return jsonify(res), res.get_http()

    return developer_view

