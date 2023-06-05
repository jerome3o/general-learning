import datetime
from typing import List

from pydantic import BaseModel
from fastapi import FastAPI, Depends
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

    @classmethod
    def create(
        cls,
        client_id: str,
        redirect_uri: str,
        user: str,
        scopes: list[str] = None,
    ):
        code = "some_random_code"
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
async def token(credentials: HTTPBasicCredentials = Depends(client_auth)):
    print(credentials)
    return {"result": "todo"}


@app.get("/client-privileged-info")
def get_privileged_info(
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
