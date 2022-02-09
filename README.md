
# Connexion Auth Paths Extended

Small connexion extension to add authentication into spec routes

The [`connexion framework`](https://github.com/zalando/connexion) it's possible to use a parameter called `auth_all_paths` (in `FlaskApp` and `AioHttpApp`), which in your documentation ([link](https://github.com/zalando/connexion/blob/2066503c5c9f30c2aaf98ad853ff8e16edd64826/connexion/apps/abstract.py#L35)) is defined as:

```text
:param auth_all_paths: whether to authenticate not defined paths
:type auth_all_paths: bool
```

And it can be used this way, during app initialization:

```python
from connexion import FlaskApp


connexion_app = FlaskApp(
    __name__,
    specification_dir='swagger/',
    auth_all_paths=True
)
```

But the only routes added to the authentication are the `404 Error route` ([link](https://github.com/zalando/connexion/blob/2066503c5c9f30c2aaf98ad853ff8e16edd64826/connexion/apis/abstract.py#L121)) routes, but there are other routes that should also be treated:

- `/openapi.json`
- `/openapi.yaml`
- `openapi_spec_path`

The idea of this extension is to apply the default authentication on these routes, without changing the behavior of anything else.

### Why?

This was once a requirement requested by the security team in an internal project. The API documentation provides very detailed technical information for the ~~attackers~~ external world, sometimes including email addresses, internal application’s url, API’s structure, and other stuffs. Think that specification it’s like a map, It's also very helpful for them to dig for vulnerabilities and detect targets.

### What about the SwaggerUI (`/ui/`) route?

It is not necessary, as it does not make much sense to ask for a auth/token on a page that will be accessed by the browser. And if some kind of authentication is required, it must be provided to consume the routes through the interface.

## Installation

Install with `pip`:

```bash
  pip install connexion-auth-paths-extd
```

## Usage/Examples

```python
from connexion.extended.auth_paths_extd import FlaskApp


connexion_app = FlaskApp(
    __name__,
    specification_dir='swagger/',
    auth_all_paths=True
)
```

Almost the same, we just change where we are importing the `FlaskApp` class from. The `auth_paths_extd.FlaskApp` object works exactly the same as `connexion.FlaskApp`, same methods, attributes and initialization. No extra parameters are needed, just pass `auth_all_paths` as `True`.

No dependencies are required in addition to the `connexion` itself.

A better exemple is on [examples folder](/example).
