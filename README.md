
# Connexion Auth Paths Extended

Small connexion extension to add authentication into spec routes

The [`connexion framework`](https://github.com/zalando/connexion) it's possible to use an parameter called `auth_all_paths` (in `FlaskApp`and `AioHttpApp`), which in your docuemntation ([link](https://github.com/zalando/connexion/blob/2066503c5c9f30c2aaf98ad853ff8e16edd64826/connexion/apps/abstract.py#L35)) is defined as:

```text
:param auth_all_paths: whether to authenticate not defined paths
:type auth_all_paths: bool
```

And it can be used this way, during app initialization:

```python
connexion_app = FlaskApp(
    __name__,
    specification_dir='.',
    auth_all_paths=True
)
```

But the only routes added to the authentication are the `404 Error route` ([link](https://github.com/zalando/connexion/blob/2066503c5c9f30c2aaf98ad853ff8e16edd64826/connexion/apis/abstract.py#L121)) routes, but there are other routes that should also be treated:

- `/openapi.json`
- `/openapi.yaml`
- `openapi_spec_path`

The idea of this extension is to apply the default authentication on these routes, without changing the behavior of anything else.

### Why?

This was once a requirement requested by the security team in a project.

### What about the UI (`/ui/`) route?

It is not necessary, as it does not make much sense to ask for a auth/token on a page that will be accessed by the browser.

## Installation

Install `connexion-auth-paths-extd` with `pip`:

```bash
  pip install connexion-auth-paths-extd
```

## Usage/Examples

```python
from connexion.extended.auth_paths_extd import FlaskApp


def create_app():
    connexion_app = FlaskApp(
        __name__,
        specification_dir='.',
        auth_all_paths=True
    )
```

A better exemple is on [examples folder](/example).
