from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    }
}

app = FastAPI()


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
