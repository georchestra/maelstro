from .models import ExceptionDetail


class MaelstroException(Exception):
    def __init__(self, **kwargs):
        self.details = ExceptionDetail(**kwargs)


class AuthError(MaelstroException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.details.status_code = 401


class UrlError(MaelstroException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.details.status_code = 404


class ParamError(MaelstroException):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.details.status_code = 400
