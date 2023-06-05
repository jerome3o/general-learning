# Mini OAuth2 setup

I really want to understand oauth better. So I'm reading the RFC and implementing a minimal setup with:

* A user agent (web fe to run in browser)
* A client
* A resource server + authentication server


This mainly just explores the happy path, only for learning so a lot of stuff is implemented poorly/missing.

## Misc notes

Query to the auth endpoint needs:
* `response_type`
* Should have `redirect_uri`


## Auth server

* Only accepts full redirect_uri's (no patterns)
* Doesn't really have scopes
* Doesn't support registering (Hard coded users / clients)
* Doesn't handle/report errors properly (if at all)
* Nothing expires yet (grants or tokens)


## Todo

* refreshing tokens
* actually use scope (don't just return everything)
