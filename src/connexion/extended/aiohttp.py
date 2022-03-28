import logging

from aiohttp import web
import aiohttp_jinja2
import jinja2
from aiohttp.web_exceptions import HTTPPermanentRedirect
from aiohttp.web_middlewares import normalize_path_middleware
from connexion.apis.aiohttp_api import AioHttpApi as _AioHttpApi
from connexion.apis.aiohttp_api import problems_middleware
from connexion.apps.aiohttp_app import AioHttpApp as _AioHttpApp
from connexion.lifecycle import ConnexionRequest

from .base import AbstractAPI


class AioHttpApi(AbstractAPI, _AioHttpApi):
    logger = logging.getLogger('connexion.apis.aiohttp_api')

    def __init__(self, *args, **kwargs):
        # NOTE we use HTTPPermanentRedirect (308) because
        # clients sometimes turn POST requests into GET requests
        # on 301, 302, or 303
        # see https://tools.ietf.org/html/rfc7538
        trailing_slash_redirect = normalize_path_middleware(
            append_slash=True,
            redirect_class=HTTPPermanentRedirect
        )
        self.subapp = web.Application(
            middlewares=[
                problems_middleware,
                trailing_slash_redirect
            ]
        )
        AbstractAPI.__init__(self, *args, **kwargs)

        aiohttp_jinja2.setup(
            self.subapp,
            loader=jinja2.FileSystemLoader(
                str(self.options.openapi_console_ui_from_dir)
            )
        )
        middlewares = self.options.as_dict().get('middlewares', [])
        self.subapp.middlewares.extend(middlewares)

    def _base_path_for_prefix(self, request):
        """
        returns a modified basePath which includes the incoming request's
        path prefix.
        """
        if isinstance(request, ConnexionRequest):
            request = request.context

        base_path = self.base_path
        if not request.path.startswith(self.base_path):
            prefix = request.path.split(self.base_path)[0]
            base_path = prefix + base_path
        return base_path

    def add_openapi_json(self):
        """
        Adds openapi json to {base_path}/openapi.json
             (or {base_path}/swagger.json for swagger2)
        """
        self.logger.debug('Adding spec json: %s/%s', self.base_path,
                     self.options.openapi_spec_path)
        self.subapp.router.add_route(
            'GET',
            self.options.openapi_spec_path,
            self._handle_spec(self._get_openapi_json)
        )

    def add_openapi_yaml(self):
        """
        Adds openapi json to {base_path}/openapi.json
             (or {base_path}/swagger.json for swagger2)
        """
        if not self.options.openapi_spec_path.endswith("json"):
            return

        openapi_spec_path_yaml = \
            self.options.openapi_spec_path[:-len("json")] + "yaml"
        self.logger.debug('Adding spec yaml: %s/%s', self.base_path,
                     openapi_spec_path_yaml)
        self.subapp.router.add_route(
            'GET',
            openapi_spec_path_yaml,
            self._handle_spec(self._get_openapi_yaml)
        )


class AioHttpApp(_AioHttpApp):
    def __init__(self, import_name, only_one_api=False, **kwargs):
        super(_AioHttpApp, self).__init__(import_name, AioHttpApi, server='aiohttp', **kwargs)
        self._only_one_api = only_one_api
        self._api_added = False
