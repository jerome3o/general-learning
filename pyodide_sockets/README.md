# Sockets in WASM with pyodide

I would like to run two little FastAPI services in the browser and have them talk to each other. With a view to using this as a tool to help understand common application web protocols like oauth.

## Rough plan

Try and monkey patch the socket library in pyodide to send bytes through the js environment to another pyodide instance.


## Some setup

### Getting pyodide served locally

from `pyodide_sockets/`

```sh
wget https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js -P site/static/
wget https://cdn.jsdelivr.net/pyodide/v0.23.0/full/python_stdlib.zip -P site/static/
```
