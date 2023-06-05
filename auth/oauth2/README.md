# Mini OAuth2 setup

I really want to understand oauth better. So I'm reading the RFC and implementing a minimal setup with:

* A user agent (web fe to run in browser)
* A client
* A resource server + authentication server


## Misc notes

Query to the auth endpoint needs:
* `response_type`
* Should have `redirect_uri`


http://localhost:8001/static/index.html?redirect_uri=http://localhost:8000/oauth2/callback&client_id=client_id&response_type=code
