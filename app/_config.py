import os

from typing import Optional
from pathlib import Path


def _get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    secret_path = Path(f"/run/secrets/{secret_name}")
    if secret_path.exists():
        return secret_path.read_text().strip()

    # Check for _FILE environment variable
    file_env = os.getenv(f"{secret_name.upper()}_FILE")
    if file_env:
        file_path = Path(file_env)
        if file_path.exists():
            return file_path.read_text().strip()

    # Fall back to direct environment variable
    env_value = os.getenv(secret_name.upper())
    if env_value:
        return env_value

    return default


FLIGHTRADAR_USERNAME = _get_secret("FLIGHTRADAR_USERNAME")
FLIGHTRADAR_PASSWORD = _get_secret("FLIGHTRADAR_PASSWORD")
FLIGHTRADAR_APP_NAME = "Flight Radar API"
