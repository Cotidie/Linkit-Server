from flask import Request
import pprint

def debug_request(request: Request, full=False):
    print("------- JSON 확인 -------")
    print(request.get_json())
    print("------- 요청 형식 --------")
    print(request.headers.get('Content-Type'))
    if full:
        print("------- 2진 데이터 확인 -------")
        print(request.get_data())
        print("------- Request 객체 확인 -------")
        print(request)
        print("------- 헤더 확인 -------")
        print(request.headers)
        print("------- Environ 확인 -------")
        print(pprint.pformat(request.environ, depth=5))