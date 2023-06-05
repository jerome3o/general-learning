from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class PrintHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = request.headers
        print("Request Headers:")
        for header, value in headers.items():
            print(f"{header}: {value}")

        response = await call_next(request)
        return response
