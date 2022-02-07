
# Connexion Auth Paths Extended - Example

Small connexion extension to add authentication into spec routes

## Run Locally

Clone the project

```bash
$ git clone https://github.com/exageraldo/connexion-auth-paths-extd.git
$ cd connexion-auth-paths-extd/
```

Go to the `example` directory

```bash
$ cd example/
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
$ FLASK_APP="app:create_app()" flask run
```
