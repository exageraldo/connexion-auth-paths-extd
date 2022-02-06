
# Connexion Auth Paths Extended

Small connexion extension to add authentication into spec routes

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
        auth_all_paths=True,
        options={
            'swagger_ui': True,
            'auth_all_paths': True
        }
    )
```

A better exemple is on [examples folder](/examples).
