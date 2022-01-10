from flask              import Flask
from flask_cors         import CORS

# Custom 라이브러리
from backend.utils import DataEncoder
from backend.database import DataBase
from backend.model    import Models
from backend.service  import UserService, LinkService, Services
from backend.view     import create_user_view, create_developer_view, create_link_view, create_group_view

# 팩토리 패턴
def create_app():
    app = Flask(__name__)
    # json 인코더 확장
    app.json_encoder = DataEncoder
    # 설정값 등록
    app.config.from_pyfile('config.py')
    app.config.db = app.config.get_namespace('MONGODB_')
    # 데이터베이스 생성
    app.db = DataBase(app.config.db.get('host'), app.config.db.get('db'))
    app.config['JWT_KEY'] = app.db.get_config('JWT_KEY')
    # MVC 패턴 적용
    ## model 레이어
    models = Models(app.db)
    ## service 레이어
    services = Services(models, app.config)
    ## view 레이어
    user_view = create_user_view(services)
    developer_view = create_developer_view(services)
    link_view = create_link_view(services)
    group_view = create_group_view(services)
    # 블루프린트 등록 => 추후 업데이트
    app.register_blueprint(user_view, url_prefix='/user')
    app.register_blueprint(developer_view, url_prefix='/developer')
    app.register_blueprint(link_view, url_prefix='/link')
    app.register_blueprint(group_view, url_prefix='/group')
    # CORS 세팅: 모든 링크를 받아들인다.
    CORS(app, resources={r'/*': {'origins': '*'}})

    # 메인페이지
    @app.route("/", methods=['GET', 'POST'])
    def hello_world():
        return "HEllo!"

    return app

