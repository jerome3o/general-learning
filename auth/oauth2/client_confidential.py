import secrets

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import requests


from common import (
    CLIENT_CONFIDENTIAL_SECRET,
    CLIENT_CONFIDENTIAL_ID,
    CLIENT_CONFIDENTIAL_REDIRECT_URI,
    CLIENT_CONFIDENTIAL_PORT,
    RESOURCE_SERVER_BASE,
)
from utils import PrintHeadersMiddleware

_secret_key = "secure-secret-key-that-isnt-hardcoded"

_session_map = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PrintHeadersMiddleware)

app.add_middleware(SessionMiddleware, secret_key=_secret_key)


@app.get("/")
async def hello():
    return {
        "service": "client_confidential",
        "CLIENT_CONFIDENTIAL_SECRET": CLIENT_CONFIDENTIAL_SECRET,
        "CLIENT_CONFIDENTIAL_ID": CLIENT_CONFIDENTIAL_ID,
        "CLIENT_CONFIDENTIAL_REDIRECT_URI": CLIENT_CONFIDENTIAL_REDIRECT_URI,
    }


app.mount("/static", StaticFiles(directory="user_agent"), name="static")


@app.get("/oauth2/info")
async def oauth2_info(request: Request):
    print(request.session)
    if "state" not in request.session:
        request.session["state"] = secrets.token_urlsafe(16)

    return {
        "state": request.session["state"],
        "redirect_uri": CLIENT_CONFIDENTIAL_REDIRECT_URI,
        "client_id": CLIENT_CONFIDENTIAL_ID,
        "response_type": "code",
        "scopes": "profile",
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
    if response.status_code != 200:
        return {"error": response.json()}

    _session_map[state] = response.json()

    return RedirectResponse(url="/static/index.html")


@app.get("/user/data")
async def user_data(request: Request):
    if "state" not in request.session or request.session["state"] not in _session_map:
        # redirect to login
        return RedirectResponse(url="/static/login.html")

    # get privileged info from resource server
    token = _session_map[request.session["state"]]["access_token"]

    # get privileged info from resource server
    # https://requests.readthedocs.io/en/master/user/authentication/#bearer-authentication
    response = requests.get(
        f"{RESOURCE_SERVER_BASE}/user-privileged-info",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    return {"data": response.json()}


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
