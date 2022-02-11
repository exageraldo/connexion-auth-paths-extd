import logging

from aiohttp import web
import aiohttp_jinja2
import jinja2
from aiohttp.web_exceptions import HTTPPermanentRedirect
from aiohttp.web_middlewares import normalize_path_middleware
from connexion.apis.flask_api import InternalHandlers as _InternalHandlers
from connexion.apis.flask_api import FlaskApi as _FlaskApi
from connexion.apis.aiohttp_api import AioHttpApi as _AioHttpApi
from connexion.apis.aiohttp_api import problems_middleware
from connexion.apis.abstract import AbstractAPIMeta as _AbstractAPIMeta
from connexion.apis.abstract import AbstractAPI as _AbstractAPI
from connexion.apps.flask_app import FlaskApp as _FlaskApp
from connexion.apps.aiohttp_app import AioHttpApp as _AioHttpApp
from connexion.operations.secure import SecureOperation
from connexion.lifecycle import ConnexionRequest
from connexion.utils import yamldumper
import flask


class InternalHandlers(_InternalHandlers):
    def get_json_spec(self, *args, **kwargs):
        return flask.jsonify(self._spec_for_prefix())

    def get_yaml_spec(self, *args, **kwargs):
        return yamldumper(self._spec_for_prefix()), 200, {"Content-Type": "text/yaml"}

class AbstractAPI(_AbstractAPI, metaclass=_AbstractAPIMeta):
    def __init__(self, specification, base_path=None, arguments=None,
                 validate_responses=False, strict_validation=False, resolver=None,
                 auth_all_paths=False, debug=False, resolver_error_handler=None,
                 validator_map=None, pythonic_params=False, pass_context_arg_name=None, options=None,
                 ):

        self._handle_spec = (
            self._mount_sec_operation_view_function if auth_all_paths
            else lambda func: func
        )
        super(AbstractAPI, self).__init__(
            specification=specification,
            base_path=base_path,
            arguments=arguments,
            validate_responses=validate_responses,
            strict_validation=strict_validation,
            resolver=resolver,
            auth_all_paths=auth_all_paths,
            debug=debug,
            resolver_error_handler=resolver_error_handler,
            validator_map=validator_map,
            pythonic_params=pythonic_params,
            pass_context_arg_name=pass_context_arg_name,
            options=options
        )

    def _mount_sec_operation_view_function(self, function):
        sec_operation = SecureOperation(
            self,
            security=self.specification.security,
            security_schemes=self.specification.security_definitions
        )
        function = sec_operation.security_decorator(function)
        function = sec_operation._request_response_decorator(function)
        return function


class FlaskApi(AbstractAPI, _FlaskApi):
    logger = logging.getLogger('connexion.apis.flask_api')

    @property
    def _handlers(self):
        # type: () -> InternalHandlers
        if not hasattr(self, '_internal_handlers'):
            self._internal_handlers = InternalHandlers(self.base_path, self.options, self.specification)
        return self._internal_handlers

    def add_openapi_json(self):
        """
        Adds spec json to {base_path}/swagger.json
        or {base_path}/openapi.json (for oas3)
        """
        self.logger.debug('Adding spec json: %s/%s', self.base_path,
                          self.options.openapi_spec_path)
        endpoint_name = f"{self.blueprint.name}_openapi_json"

        self.blueprint.add_url_rule(
            self.options.openapi_spec_path,
            endpoint_name,
            self._handle_spec(self._handlers.get_json_spec)
        )

    def add_openapi_yaml(self):
        """
        Adds spec yaml to {base_path}/swagger.yaml
        or {base_path}/openapi.yaml (for oas3)
        """
        if not self.options.openapi_spec_path.endswith("json"):
            return

        openapi_spec_path_yaml = \
            self.options.openapi_spec_path[:-len("json")] + "yaml"
        self.logger.debug('Adding spec yaml: %s/%s', self.base_path,
                          openapi_spec_path_yaml)
        endpoint_name = f"{self.blueprint.name}_openapi_yaml"
        self.blueprint.add_url_rule(
            openapi_spec_path_yaml,
            endpoint_name,
            self._handle_spec(self._handlers.get_yaml_spec)
        )


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


class FlaskApp(_FlaskApp):
    def __init__(self, import_name, server='flask', **kwargs):
        super(_FlaskApp, self).__init__(import_name,
                                       FlaskApi, server=server, **kwargs)


class AioHttpApp(_AioHttpApp):
    def __init__(self, import_name, only_one_api=False, **kwargs):
        super(_AioHttpApp, self).__init__(import_name, AioHttpApi, server='aiohttp', **kwargs)
        self._only_one_api = only_one_api
        self._api_added = False
