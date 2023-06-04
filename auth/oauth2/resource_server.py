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


@app.get("/")
async def hello():
    return _registered_clients


@app.get("/privileged-info")
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
    )


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
