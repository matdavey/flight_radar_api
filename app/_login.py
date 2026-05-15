from fastapi import APIRouter
from loguru import logger
from pyflightdata import FlightData

from app import _config as config

router = APIRouter()


@router.get("/get_client", tags=["login"])
def get_client():
    flight_radar = FlightData()
    flight_radar.login(config.FLIGHTRADAR_USERNAME, config.FLIGHTRADAR_PASSWORD)
    return flight_radar
