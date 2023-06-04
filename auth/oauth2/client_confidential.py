from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common import (
    CLIENT_CONFIDENTIAL_SECRET,
    CLIENT_CONFIDENTIAL_ID,
    CLIENT_CONFIDENTIAL_REDIRECT_URI,
    CLIENT_CONFIDENTIAL_PORT,
)

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
    return {
        "service": "client_confidential",
        "CLIENT_CONFIDENTIAL_SECRET": CLIENT_CONFIDENTIAL_SECRET,
        "CLIENT_CONFIDENTIAL_ID": CLIENT_CONFIDENTIAL_ID,
        "CLIENT_CONFIDENTIAL_REDIRECT_URI": CLIENT_CONFIDENTIAL_REDIRECT_URI,
    }


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
