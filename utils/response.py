from backend.utils.enums import Category


class Status:
    # [메시지, 성공여부, HTTP코드]
    # 코드가 0이면 항상 Global이다.
    DATA = {
        Category.Global: {
            0: ["정상 동작", True, 200],
            1: ["JSON 미전달", False, 400],
            2: ["불완전한 데이터", False, 400],
            3: ["토큰 미전달", False, 401],
            4: ["만료된 토큰", False, 401],
            5: ["CRUD 연산에 실패했습니다.", False, 400]
        },
        Category.User: {
            1: ["이메일이 중복되었습니다.", False, 400],
            2: ["일치하는 유저를 찾지 못했습니다.", False, 400],
            3: ["비밀번호가 일치하지 않습니다.", False, 401],
            4: ["토큰이 유효하지 않습니다.", False, 401]
        },
        Category.Link: {
            1: ["링크는 반드시 속한 그룹, 폴더가 존재해야 합니다.", False, 400],
            2: ["해당하는 폴더/파일이 존재하지 않습니다.", False, 400],
            3: ["루트 폴더에는 한꺼번에 여러 폴더를 생성할 수 없습니다.", False, 400],
            4: ["폴더/링크 수정에 실패했습니다.", False, 500]
        },
        Category.Group: {
            1: ["유효한 gid가 아닙니다.", False, 400],
            2: ["유효한 유저가 아닙니다.", False, 400]
        }
    }

    def __init__(self, cat=Category.Global, code=0):
        self.cat = cat
        self.code = None
        self.msg = None
        self._http = None
        self._success = None

        self.set_code(code, is_global=(code == 0))

    def set_code(self, code, is_global=False):
        data = self._find_data(code, is_global)
        if not data:
            raise KeyError(f"상태코드 {self.cat.value+code}가 정의되지 않았습니다.")

        prefix_value = 0 if is_global else self.cat.value
        self.code = code + prefix_value
        self.msg = data[0]
        self._success = data[1]
        self._http = data[2]

    def _find_data(self, code, is_global=False):
        cat = Category.Global if is_global else self.cat
        dict = Status.DATA[cat]
        return dict.get(code, None)

    @property
    def success(self):
        return self._success

    @property
    def http(self):
        return self._http


class Response():
    def __init__(self, cat: Category = Category.Global, code=0):
        self.status = Status(cat=cat, code=code)
        self.data = dict()

    def get_http(self):
        return self.status.http

    def to_dict(self):
        return {
            'success': self.status.success,
            'status': self.status.code,
            'msg': self.status.msg,
            'res_data': self.data
        }

    def __str__(self):
        success = "성공" if self.status.success else "실패"
        msg = self.status.msg

        return f"요청 {success}, {msg}"
