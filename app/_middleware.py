import time
import uuid
from datetime import datetime, timezone

from fastapi import Request
from loguru import logger
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware


async def add_elapsed_header(request: Request, call_next):
    """
    Middleware that adds a HTTP header containing how long it took
    us to process this request in seconds
    """
    ts = time.perf_counter()
    response = await call_next(request)
    te = time.perf_counter()
    response.headers["X-Elapsed"] = f"{te-ts:.2f}"
    return response


ElapsedMiddleware = Middleware(BaseHTTPMiddleware, dispatch=add_elapsed_header)


def get_client_addr(client):
    if not client:
        return

    addr = client.host or ""
    if client.port:
        addr += ":" + str(client.port)

    return addr


def get_path_with_query_string(url):
    path_with_query_string = url.path
    if url.query:
        path_with_query_string = f"{path_with_query_string}?{url.query}"

    return path_with_query_string


async def access_log(request: Request, call_next):
    """
    Emits a log message summarising each HTTP request

    Similar to uvicorn's access log with the addition of log context
    about the request, response and includes custom headers
    """
    req = {
        "client_ip": get_client_addr(request.client),
        "method": request.method,
        "version": request.scope.get("http_version", ""),
        "path": get_path_with_query_string(request.url),
    }
    with logger.contextualize(req=req):
        response = await call_next(request)

        # Identify the FastAPI endpoint that processed this request
        # eg. /scan/{scan_id}
        route = request.scope.get("route")
        if route:
            path = getattr(route, "path", None)
            if path:
                req["handler"] = path

        res = {"status_code": response.status_code}
        try:
            res["error"] = request.state.error
        except AttributeError:
            pass

        custom_headers = {
            header.removeprefix("x-").replace("-", "_"): value
            for header, value in response.headers.items()
            if header.startswith("x-")
        }

        logger.bind(**custom_headers).bind(res=res).info(
            f'{req["client_ip"]} - "{req["method"]} {req["path"]} HTTP/{req["version"]}" {res["status_code"]}'
        )

        return response


AccessLogMiddleware = Middleware(BaseHTTPMiddleware, dispatch=access_log)

ACTIVE_REQUESTS = {}


async def track_active_requests(request: Request, call_next):
    global ACTIVE_REQUESTS

    req = {
        "start": datetime.now(timezone.utc).isoformat(),
        "client_ip": get_client_addr(request.client),
        "method": request.method,
        "path": get_path_with_query_string(request.url),
    }

    request_id = str(uuid.uuid4())
    ACTIVE_REQUESTS[request_id] = req
    request.state.active_requests = ACTIVE_REQUESTS
    response = await call_next(request)
    del ACTIVE_REQUESTS[request_id]
    return response


TrackActiveRequestsMiddleware = Middleware(BaseHTTPMiddleware, dispatch=track_active_requests)
