from contextvars import ContextVar

_current_request_id: ContextVar[str | None] = ContextVar('current_request_id', default=None)


def set_current_request_id(request_id: str):
    return _current_request_id.set(request_id)


def reset_current_request_id(token):
    _current_request_id.reset(token)


def get_current_request_id() -> str | None:
    return _current_request_id.get()
