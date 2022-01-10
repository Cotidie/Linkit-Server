class CustomException(Exception):
    """
        오류코드를 갖기 위한 간단한 예외 클래스
    """
    def __init__(self, code, is_global=False, message="비정상 동작"):
        self.code = code
        self.is_global = is_global
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"오류: {self.message}"