from fastapi import Request, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED


class PrintHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = request.headers
        print("Request Headers:")
        for header, value in headers.items():
            print(f"{header}: {value}")

        response = await call_next(request)
        return response


# little basic authentication middleware
# https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/


class HTTPBasicWithAuth(HTTPBasic):
    def __init__(
        self, scheme_name: str = None, auto_error: bool = True, users: dict = None
    ):
        if users is None:
            users = {"user1": "password1"}
        self.users = users
        super().__init__(scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPBasicCredentials:
        credentials: HTTPBasicCredentials = await super().__call__(request)

        if credentials.username not in self.users:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        if credentials.password != self.users[credentials.username]:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )

        return credentials
