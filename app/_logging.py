import json
import logging
import sys
import traceback
import warnings

from fastapi.encoders import jsonable_encoder
from loguru import logger

# Set of the default fields on a logging.LogRecord
LOG_FIELDS = set(logging.makeLogRecord({}).__dict__.keys())


class InterceptHandler(logging.Handler):
    """
    Intercepts logs sent to the python logging system and forwards them to loguru.
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Pass through extra context.
        # Extra fields are merged into logging.LogRecord so we
        # extract any field that isn't in the default LogRecord
        # and pass through as extra
        extra = {field: value for field, value in record.__dict__.items() if field not in LOG_FIELDS}

        logger.bind(**extra).opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def sink_serializer(message):
    """
    Custom serialiser that supports Pydantic models
    """
    record = message.record

    simplified = {
        "level": record["level"].name,
        "message": record["message"],
        "pid": record["process"].id,
        "tid": record["thread"].id,
        "name": record["name"],
        "fn": record["function"],
        "path": record["file"].path,
        "line": record["line"],
        "timestamp": record["time"].isoformat(),
        "extra": record["extra"],
    }

    exc_info = record.get("exception")
    if exc_info:
        # Exception could be a loguru.RecordException named tuple
        # or it could be exc_info from the standard logger
        # which is a normal tuple
        try:
            exc_type, exception, tb = exc_info
            simplified["exception"] = str(exception)
            simplified["exception.type"] = str(exc_type)
            simplified["exception.stack"] = "".join(traceback.format_tb(tb))
        except Exception:
            simplified["exception"] = str(exc_info)

    # Convert the log into something jsonable
    log_msg = jsonable_encoder(simplified)

    # And log as json. Print will flush because it adds a new line
    print(json.dumps(log_msg), file=sys.stderr)


def walk(obj, path=None):
    if path is None:
        path = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk(value, path + [key])
    elif isinstance(obj, list):
        for n, value in enumerate(obj):
            yield from walk(value, path + [str(n)])
    else:
        yield ".".join(path), str(obj)


def log_fmt(fields, hide_fields):
    pairs = [f"{field}={value}" for field, value in walk(fields) if field not in hide_fields]

    return " ".join(sorted(pairs))


# Uvicorn's logging passes a logging message with color as an extra field
LOG_FIELDS_TO_HIDE = {"color_message"}


def console_formatter(record):
    """
    A log formatter similar to uvicorn except it includes any extra context
    in the log message using logfmt for readability
    """

    msg = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{message}</level>"

    context = log_fmt(record["extra"], hide_fields=LOG_FIELDS_TO_HIDE)
    if context:
        record["context"] = context
        msg = msg + " <dim>{context}</dim>"

    exception = record.get("exception")
    if exception:
        msg = msg + "\n{exception}"

    return msg + "\n"


def setup_logging(log_level="INFO", log_json=True):
    # Suppress Python's resource warnings that python thinks are long lived and haven't been released
    # which happens because urllib3 maintains the connection as part of the connection pool.
    # This warning triggers a lot during the export which fetches scans from s3.
    # See https://gitlab.com/lodestonelabs/karma/-/issues/87
    # and https://github.com/boto/boto3/issues/454
    warnings.filterwarnings("ignore", category=ResourceWarning)

    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.getLevelName(log_level))

    # remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Disable the access log as we add our own
    logging.getLogger("uvicorn.access").propagate = False

    # configure loguru
    handler = {"sink": sys.stderr}
    if log_json:
        handler["sink"] = sink_serializer
    else:
        handler["colorize"] = sys.stderr.isatty()
        handler["format"] = console_formatter

    logger.configure(handlers=[handler])
