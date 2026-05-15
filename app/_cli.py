import asyncio
import secrets

import hupper
import typer
import uvicorn
from dotenv import load_dotenv

from app._logging import setup_logging

app = typer.Typer()


def get_private_ip() -> str:
    import ipaddress
    from netifaces import interfaces, ifaddresses, AF_INET

    for interface in interfaces():
        addresses = ifaddresses(interface)
        for link in addresses.get(AF_INET, []):
            ip = ipaddress.ip_address(link["addr"])
            if ip.is_private and not ip.is_loopback and not ip.is_link_local:
                return str(ip)

    raise RuntimeError("Could not detect a private IP")


@app.callback()
def handle_dotenv():
    load_dotenv()


@app.command()
def run(
    host: str = "0.0.0.0",
    port: int = 8006,
    reload: bool = False,
    log_json: bool = False,
) -> None:
    if reload:
        hupper.start_reloader("app._cli.run", worker_kwargs={"host": host, "port": port, "log_json": log_json})

    if host == "private":
        host = get_private_ip()

    config = uvicorn.Config(
        "app._fastapi:app",
        host=host,
        port=port,
        log_level="info",
        access_log=False,  # We will add our own
        log_config=None,
        timeout_keep_alive=400,
    )
    server = uvicorn.Server(config)
    setup_logging(log_json=log_json)
    server.run()
