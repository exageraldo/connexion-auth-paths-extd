from connexion.extended.aiohttp import AioHttpApp


def create_app(argv):
    connexion_app = AioHttpApp(
        __name__,
        specification_dir='.',
        auth_all_paths=True
    )

    connexion_app.add_api(
        'openapi.yml',
        base_path='/v1'
    )
    return connexion_app.app
