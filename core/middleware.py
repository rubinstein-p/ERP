import uuid

from core.request_context import reset_current_request_id, set_current_request_id


class RequestIdMiddleware:
    """
    Inyecta un request_id unico por request para correlacionar auditoria y trazas.
    """

    header_name = 'X-Request-ID'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        request.request_id = request_id
        token = set_current_request_id(request_id)

        try:
            response = self.get_response(request)
        finally:
            reset_current_request_id(token)

        response[self.header_name] = request_id
        return response
