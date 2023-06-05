import datetime

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

from common import (
    CLIENT_CONFIDENTIAL_SECRET,
    CLIENT_CONFIDENTIAL_ID,
    CLIENT_CONFIDENTIAL_REDIRECT_URI,
    RESOURCE_SERVER_PORT,
)
from utils import PrintHeadersMiddleware

_registered_clients = {
    CLIENT_CONFIDENTIAL_ID: {
        "client_id": CLIENT_CONFIDENTIAL_ID,
        "client_secret": CLIENT_CONFIDENTIAL_SECRET,
        "redirect_uris": [CLIENT_CONFIDENTIAL_REDIRECT_URI],
        "scopes": ["profile"],
        "priviliged_info": f"This is priviliged info for {CLIENT_CONFIDENTIAL_ID}",
    }
}

app = FastAPI()
security = HTTPBasic()

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
    return {"registered_clients": _registered_clients}


# authorisation endpoint
@app.get("/oauth2/authorize")
async def authorize():
    return {"result": "todo"}


# token endpoint
@app.post("/oauth2/token")
async def token():
    return {"result": "todo"}


@app.get("/client-privileged-info")
def get_privileged_info(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
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
