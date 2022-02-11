from connexion.extended.auth_paths_extd import FlaskApp


def create_app():
    connexion_app = FlaskApp(
        __name__,
        specification_dir='.',
        auth_all_paths=True
    )

    connexion_app.add_api(
        'openapi.yml',
        base_path='/v1'
    )
    return connexion_app.app
