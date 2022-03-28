from connexion.apis.abstract import AbstractAPIMeta as _AbstractAPIMeta
from connexion.apis.abstract import AbstractAPI as _AbstractAPI
from connexion.operations.secure import SecureOperation


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
