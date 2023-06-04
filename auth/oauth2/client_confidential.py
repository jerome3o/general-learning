from fastapi import FastAPI
from common import (
    CLIENT_CONFIDENTIAL_SECRET,
    CLIENT_CONFIDENTIAL_ID,
    CLIENT_CONFIDENTIAL_REDIRECT_URI,
    CLIENT_CONFIDENTIAL_PORT,
)

app = FastAPI()


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
