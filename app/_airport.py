from fastapi import APIRouter
from loguru import logger

from app import _config as config, _login as login

router = APIRouter()


@router.get("/get_airports", tags=["airport"])
def get_airports(country: str):
    flight_radar_client = login.get_client()
    return flight_radar_client.airports(country)


@router.get("/get_arrivals", tags=["airport"])
def get_arrivals(airport_code: str):
    flight_radar_client = login.get_client()
    return flight_radar_client.get_airport_arrivals(airport_code)


@router.get("/get_departures", tags=["airport"])
def get_departures(airport_code: str):
    flight_radar_client = login.get_client()
    return flight_radar_client.get_airport_departures(airport_code)


@router.get("/get_details", tags=["airport"])
def get_departures(airport_code: str):
    flight_radar_client = login.get_client()
    return flight_radar_client.get_airport_details(airport_code)


@router.get("/get_weather", tags=["airport"])
def get_departures(airport_code: str):
    flight_radar_client = login.get_client()
    return flight_radar_client.get_airport_weather(airport_code)
