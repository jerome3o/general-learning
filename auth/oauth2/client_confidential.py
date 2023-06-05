from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import requests

from common import (
    CLIENT_CONFIDENTIAL_SECRET,
    CLIENT_CONFIDENTIAL_ID,
    CLIENT_CONFIDENTIAL_REDIRECT_URI,
    CLIENT_CONFIDENTIAL_PORT,
    RESOURCE_SERVER_BASE,
)
from utils import PrintHeadersMiddleware

app = FastAPI()

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
        "service": "client_confidential",
        "CLIENT_CONFIDENTIAL_SECRET": CLIENT_CONFIDENTIAL_SECRET,
        "CLIENT_CONFIDENTIAL_ID": CLIENT_CONFIDENTIAL_ID,
        "CLIENT_CONFIDENTIAL_REDIRECT_URI": CLIENT_CONFIDENTIAL_REDIRECT_URI,
    }


@app.get("/oauth2/callback")
async def oauth2_callback(code: str, state: str):
    # exchange code for token
    # https://requests.readthedocs.io/en/master/user/quickstart/#custom-headers
    response = requests.post(
        f"{RESOURCE_SERVER_BASE}/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": CLIENT_CONFIDENTIAL_REDIRECT_URI,
        },
        auth=(CLIENT_CONFIDENTIAL_ID, CLIENT_CONFIDENTIAL_SECRET),
    )

    # get privileged info from resource server
    # https://requests.readthedocs.io/en/master/user/authentication/#bearer-authentication
    response = requests.get(
        f"{RESOURCE_SERVER_BASE}/user-privileged-info",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {response.json()['access_token']}",
        },
    )

    return {"response_from_auth": response.json()}


@app.get("/client-privileged-info")
def get_privileged_info(with_auth: bool = True):
    # get privileged info from resource server to demonstrate basic auth
    # https://requests.readthedocs.io/en/master/user/authentication/#basic-authentication
    if with_auth:
        response = requests.get(
            f"{RESOURCE_SERVER_BASE}/client-privileged-info",
            auth=(CLIENT_CONFIDENTIAL_ID, CLIENT_CONFIDENTIAL_SECRET),
            # auth=("sdfsdfsdf", "sdfsdfs"),
            # auth=(CLIENT_CONFIDENTIAL_ID, "sdfsdfs"),
        )
    else:
        response = requests.get(f"{RESOURCE_SERVER_BASE}/privileged-info")
    return response.json()


def main():
    import uvicorn

    uvicorn.run(
        "client_confidential:app",
        host="localhost",
        reload=True,
        port=CLIENT_CONFIDENTIAL_PORT,
    )


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
