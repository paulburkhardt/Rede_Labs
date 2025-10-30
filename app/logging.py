from fastapi import Request
from http import HTTPStatus
import logging

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
MAX_LOG_BODY = 2048  # bytes of decoded text to log

logger = logging.getLogger("request_body")

logger.setLevel(logging.INFO)

# Only add a handler if none present (avoid duplicates in reload)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s %(message)s"))  # timestamp first
    logger.addHandler(_h)
    logger.propagate = False  # don’t bubble to root/uvicorn

async def access_log_with_optional_body(request: Request, call_next):
    # Capture client address (respect proxy headers if present)
    xff = request.headers.get("x-forwarded-for")
    xfp = request.headers.get("x-forwarded-port")
    if xff:
        client_ip = xff.split(",")[0].strip()
        client_port = xfp or "-"
        client_addr = f"{client_ip}:{client_port}"
    else:
        client_addr = (
            f"{request.client.host}:{request.client.port}"
            if request.client
            else "-"
        )

    # Request line (include query if present)
    path = request.url.path
    if request.url.query:
        path = f"{path}?{request.url.query}"
    http_version = request.scope.get("http_version", "1.1")
    request_line = f'{request.method} {path} HTTP/{http_version}'

    # If method can have a body, read and re-inject so downstream can still read it
    body_bytes = b""
    if request.method in WRITE_METHODS:
        body_bytes = await request.body()

        send_body = body_bytes

        async def receive():
            nonlocal send_body
            chunk, send_body = send_body, b""
            return {"type": "http.request", "body": chunk, "more_body": False}

        request = Request(request.scope, receive=receive)

    # Process request
    response = await call_next(request)

    # Status code + reason phrase (best-effort)
    status = response.status_code
    try:
        reason = HTTPStatus(status).phrase
    except ValueError:
        reason = ""

    # Decide whether/how to render the body
    body_str = ""
    if body_bytes:
        ctype = request.headers.get("content-type", "")
        # Try to decode only for text-like content; otherwise show size & type
        if ctype.startswith(("application/json", "text/")):
            txt = body_bytes.decode("utf-8", errors="replace")
            if len(txt) > MAX_LOG_BODY:
                txt = txt[: MAX_LOG_BODY - 3] + "..."
            body_str = f" body={txt}"
        else:
            body_str = f" body=<{len(body_bytes)} bytes, {ctype or 'unknown content-type'}>"

    # Single merged line: timestamp is provided by the logger formatter
    logger.info('%s - "%s" %d%s%s',
                client_addr,
                request_line,
                status,
                f" {reason}" if reason else "",
                body_str)

    return response
