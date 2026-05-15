import os
import time
import json
import atexit
import os.path
from datetime import datetime, timezone

from loguru import logger
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import StreamingResponse

from app import (
    _middleware as middleware,
    _login as login,
    _config as config,
    _airport as airport,
    _flights as flights,
)


load_dotenv()


app = FastAPI(
    title=config.FLIGHTRADAR_APP_NAME,
    middleware=[
        middleware.AccessLogMiddleware,
        middleware.ElapsedMiddleware,
        middleware.TrackActiveRequestsMiddleware,
    ],
)

app.include_router(
    login.router,
    prefix="/login",
    tags=["login"],
    responses={418: {"description": "I'm a teapot"}},
)


app.include_router(
    airport.router,
    prefix="/airport",
    tags=["airport"],
    responses={418: {"description": "I'm a teapot"}},
)

app.include_router(
    flights.router,
    prefix="/flights",
    tags=["flights"],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/health")
def get_health():
    return {
        "now": datetime.now(timezone.utc).isoformat(),
        "status": "OK",
    }
