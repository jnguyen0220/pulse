import aiohttp
import socket
import asyncio
from nicegui import run

headers = {"User-Agent": "Mozilla 5.0"}
error = None


async def http_ping_wrapper(id: int, func: callable):
    error = None
    resp = None
    try:
        resp = await func
        if resp.status != 200:
            error = resp.reason
    except Exception as msg:
        error = msg
    finally:
        if resp:
            resp.close()
    return id, error


async def web_ping(hosts: list[tuple]):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[
                http_ping_wrapper(
                    id=id,
                    func=session.get(host, headers=headers),
                )
                for id, host in hosts
            ],
        )


async def tcp_ping(hosts: list[tuple]):
    return await asyncio.gather(
        *[
            run.io_bound(tcp_pin_wrapper, id=id, host=host, port=port)
            for id, host, port in hosts
        ],
    )


def tcp_pin_wrapper(id: int, host: str, port: int, timeout: int = 1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    error = None
    try:
        sock.connect((host, port))
    except socket.error as msg:
        error = msg
    finally:
        sock.close()
    return id, error
