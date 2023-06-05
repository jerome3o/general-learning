import datetime
from typing import List
import secrets

from pydantic import BaseModel
from fastapi import FastAPI, Depends, Form, Header, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from typing_extensions import Annotated

from common import (
    CLIENT_CONFIDENTIAL_SECRET,
    CLIENT_CONFIDENTIAL_ID,
    CLIENT_CONFIDENTIAL_REDIRECT_URI,
    RESOURCE_SERVER_PORT,
)
from utils import PrintHeadersMiddleware, HTTPBasicWithAuth

_DEFAULT_SCOPES = ["profile"]


class AuthorisationRequest(BaseModel):
    redirect_uri: str
    client_id: str
    response_type: str


# information to be stored on the server
class AuthorisationCodeGrant(BaseModel):
    code: str
    user: str
    scopes: list[str]
    client_id: str
    redirect_uri: str
    expires: datetime.datetime
    state: str = None

    @classmethod
    def create(
        cls,
        client_id: str,
        redirect_uri: str,
        user: str,
        scopes: list[str] = None,
    ):
        code = secrets.token_urlsafe(32)
        scopes = scopes or _DEFAULT_SCOPES
        expires = datetime.datetime.now() + datetime.timedelta(minutes=5)
        return cls(
            code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
            expires=expires,
            user=user,
            scopes=scopes,
        )


class AccessTokenDto(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scopes: list[str]
    user: str
    client_id: str
    expires: datetime.datetime

    @classmethod
    def create(
        cls,
        client_id: str,
        user: str,
        scopes: list[str] = None,
    ):
        token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires = datetime.datetime.now() + datetime.timedelta(minutes=5)
        return cls(
            access_token=token,
            token_type="bearer",
            client_id=client_id,
            expires_in=3600,
            refresh_token=refresh_token,
            user=user,
            scopes=scopes or _DEFAULT_SCOPES,
            expires=expires,
        )

    def to_dto(self) -> AccessTokenDto:
        return AccessTokenDto(
            access_token=self.access_token,
            token_type=self.token_type,
            expires_in=self.expires_in,
            refresh_token=self.refresh_token,
        )


_registered_clients = {
    CLIENT_CONFIDENTIAL_ID: {
        "client_id": CLIENT_CONFIDENTIAL_ID,
        "client_secret": CLIENT_CONFIDENTIAL_SECRET,
        "redirect_uris": [CLIENT_CONFIDENTIAL_REDIRECT_URI],
        "scopes": ["profile"],
        "priviliged_info": f"This is priviliged info for {CLIENT_CONFIDENTIAL_ID}",
    }
}

_registered_users = {
    "user1": {
        "username": "user1",
        "password": "password1",
        "first_name": "User",
        "last_name": "One",
        "scopes": ["profile"],
        "privileged_info": "This is priviliged info for user1",
    },
    "user2": {
        "username": "user2",
        "password": "password2",
        "first_name": "User",
        "last_name": "Two",
        "scopes": ["profile"],
        "privileged_info": "This is priviliged info for user2",
    },
}

_authorization_codes: List[AuthorisationCodeGrant] = []

_access_tokens = []

app = FastAPI()
client_auth = HTTPBasicWithAuth(
    users={c: v["client_secret"] for c, v in _registered_clients.items()}
)
user_auth = HTTPBasicWithAuth(
    users={c: v["password"] for c, v in _registered_users.items()}
)

app.mount("/static", StaticFiles(directory="auth_fe"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrintHeadersMiddleware)


@app.get("/")
async def hello():
    return {
        "registered_clients": _registered_clients,
        "registered_users": _registered_users,
    }


@app.get("/oauth2/authorize")
async def oauth2_authorize(request: Request):
    print(request.query_params)
    # serve the /static/index.html file
    return RedirectResponse(
        url=f"/static/index.html?{request.query_params}",
        status_code=303,
    )


# client authorisation endpoint
@app.post("/oauth2/authorize")
async def login(
    info: AuthorisationRequest,
    credentials: HTTPBasicCredentials = Depends(user_auth),
):
    # assert that the client is registered
    if info.client_id not in _registered_clients:
        return {
            "result": "failure",
            "output": f"client {info.client_id} not registered",
        }

    # assert the redirect uri is registered for the client
    if info.redirect_uri not in _registered_clients[info.client_id]["redirect_uris"]:
        return {
            "result": "failure",
            "output": (
                f"redirect_uri {info.redirect_uri} "
                f"not registered for client {info.client_id}"
            ),
        }

    # create an authorisation code
    code = AuthorisationCodeGrant.create(
        client_id=info.client_id,
        redirect_uri=info.redirect_uri,
        user=credentials.username,
    )
    _authorization_codes.append(code)

    # todo understand state
    return RedirectResponse(
        url=f"{info.redirect_uri}?code={code.code}&state=xyz", status_code=303
    )


# token endpoint
@app.post("/oauth2/token")
async def token(
    code: Annotated[str, Form(...)],
    redirect_uri: Annotated[str, Form(...)],
    grant_type: Annotated[str, Form(...)],
    credentials: HTTPBasicCredentials = Depends(client_auth),
):
    # we know this is ok because of the middleware
    client = _registered_clients[credentials.username]

    auth_code: AuthorisationCodeGrant = next(
        (c for c in _authorization_codes if c.code == code), None
    )

    if not auth_code:
        return {
            "result": "failure",
            "output": f"no auth code found for {code}",
        }

    if auth_code.client_id != client["client_id"]:
        return {
            "result": "failure",
            "output": f"client id mismatch for {code}",
        }

    if auth_code.redirect_uri != redirect_uri:
        return {
            "result": "failure",
            "output": f"redirect uri mismatch for {code}",
        }

    # create an access token
    token = AccessToken.create(
        client_id=client["client_id"],
        user=auth_code.user,
        scopes=auth_code.scopes,
    )
    _access_tokens.append(token)

    return token.to_dto()


@app.get("/user-privileged-info")
def get_privileged_user_info(authorization: Annotated[str, Header()]):
    # strip Bearer from the header
    authorization = authorization.split(" ")[1]

    # check if the token is valid
    token: AccessToken = next(
        (t for t in _access_tokens if t.access_token == authorization), None
    )

    if not token:
        return {
            "result": "failure",
            "output": f"no token found for {authorization}",
        }

    if token.expires < datetime.datetime.now():
        return {
            "result": "failure",
            "output": f"token expired for {authorization}",
        }

    return {
        "authorization": authorization,
        "result": "success",
        "output": _registered_users["user1"]["privileged_info"]
        + " "
        + str(datetime.datetime.now()),
    }


@app.get("/client-privileged-info")
def get_privileged_client_info(
    credentials: Annotated[HTTPBasicCredentials, Depends(client_auth)]
):
    if credentials.username not in _registered_clients:
        return {
            "result": "failure",
            "output": f"client {credentials.username} not registered",
        }

    client = _registered_clients[credentials.username]
    if client["client_secret"] != credentials.password:
        return {
            "result": "failure",
            "output": f"incorrect client secret for {credentials.username}",
        }

    # with current time appended
    return {
        "result": "success",
        "output": _registered_clients[CLIENT_CONFIDENTIAL_ID]["priviliged_info"]
        + " "
        + str(datetime.datetime.now()),
    }


def main():
    import uvicorn

    uvicorn.run(
        "resource_server:app",
        host="localhost",
        reload=True,
        port=RESOURCE_SERVER_PORT,
        log_level="debug",
    )


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
