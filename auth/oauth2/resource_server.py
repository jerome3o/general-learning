import datetime

from pydantic import BaseModel
from fastapi import FastAPI, Depends
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


class AuthenticationRequest(BaseModel):
    username: str
    password: str
    redirect_uri: str
    client_id: str
    response_type: str


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

app = FastAPI()
client_auth = HTTPBasicWithAuth(
    users={c: _registered_clients[c]["client_secret"] for c in _registered_clients}
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
async def login(info: AuthenticationRequest):
    print(info)
    return {"result": "todo"}


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
