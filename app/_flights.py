from fastapi import APIRouter, Path
from loguru import logger

from typing import Annotated
from pydantic import BaseModel, Field


from app import _config as config, _login as login

router = APIRouter()


@router.get("/get_flights", tags=["flights"])
def get_flights(flight_number: str = Annotated[str, Path(..., title="The Flight ID")]):
    flight_radar_client = login.get_client()
    return flight_radar_client.get_flights(flight_number)


class FlightDate(BaseModel):
    flght_date: str = Field(default=None, title="Date String in the format yyyymmdd")


class FlightDate:
    flight_number: str
    flight_date: str


@router.get("/get_flight_for_date", tags=["flights"])
def get_flight(
    flight_number: str = Annotated[str, Path(..., title="The Flight ID")],
    flight_date: str = Annotated[str, Path(..., title="The date of the flight format in yyyymmdd")],
):
    flight_radar_client = login.get_client()
    return flight_radar_client.get_flight_for_date(flight_number, flight_date)


@router.get("/get_flight_to_from", tags=["flights"])
def get_flight_from_to(
    origin: str = Annotated[str, Path(..., title="IATA 3 letter code for the origin airport")],
    destination: str = Annotated[str, Path(..., title="IATA 3 letter code for the departure airport")],
):
    flight_radar_client = login.get_client()
    return flight_radar_client.get_flights_from_to(origin, destination)
