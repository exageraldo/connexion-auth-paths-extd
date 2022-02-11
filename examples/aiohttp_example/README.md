
# Connexion Auth Paths Extended - Example

Small connexion extension to add authentication into spec routes

## Run Locally

Clone the project

```bash
$ git clone https://github.com/exageraldo/connexion-auth-paths-extd.git
$ cd connexion-auth-paths-extd/
```

Go to the `examples/aiohttp_example` directory

```bash
$ cd examples/aiohttp_example/
```

Create a virtual env
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Install dependencies

```bash
$ pip install -r requirements.txt
```

Start the server

```bash
$ python -m aiohttp.web -H localhost -P 8080 package.module:init_func
```
