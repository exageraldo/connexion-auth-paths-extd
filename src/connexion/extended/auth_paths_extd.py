import logging

from connexion.apis.flask_api import InternalHandlers as _InternalHandlers
from connexion.apis.flask_api import FlaskApi as _FlaskApi
from connexion.apps.flask_app import FlaskApp as _FlaskApp
from connexion.operations.secure import SecureOperation
from connexion.utils import yamldumper
import flask


class InternalHandlers(_InternalHandlers):
    def get_json_spec(self, *args, **kwargs):
        return flask.jsonify(self._spec_for_prefix())

    def get_yaml_spec(self, *args, **kwargs):
        return yamldumper(self._spec_for_prefix()), 200, {"Content-Type": "text/yaml"}


class FlaskApi(_FlaskApi):
    logger = logging.getLogger('connexion.apis.flask_api')

    @property
    def _handlers(self):
        # type: () -> InternalHandlers
        if not hasattr(self, '_internal_handlers'):
            self._internal_handlers = InternalHandlers(self.base_path, self.options, self.specification)
        return self._internal_handlers

    def _mount_view_function(self, function):
        if self.options.as_dict().get('auth_all_paths'):
            sec_operation = SecureOperation(
                self,
                security=self.specification.security,
                security_schemes=self.specification.security_definitions
            )
            function = sec_operation.security_decorator(function)
            function = sec_operation._request_response_decorator(function)
        return function

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
            self._mount_view_function(self._handlers.get_json_spec)
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
            self._mount_view_function(self._handlers.get_yaml_spec)
        )


class FlaskApp(_FlaskApp):
    def __init__(self, import_name, server='flask', **kwargs):
        super(_FlaskApp, self).__init__(import_name,
                                       FlaskApi, server=server, **kwargs)
