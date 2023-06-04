# Confidential refers to the oauth client type

RESOURCE_SERVER_PORT = 8001

# Assume already registered
CLIENT_CONFIDENTIAL_PORT = 8000
CLIENT_CONFIDENTIAL_SECRET = "client_confidential_secret"
CLIENT_CONFIDENTIAL_ID = "client_confidential_id"
CLIENT_CONFIDENTIAL_REDIRECT_URI = (
    f"http://localhost:{CLIENT_CONFIDENTIAL_PORT}/oauth2/callback"
)
