from http import HTTPStatus
from aiohttp.web import Response


async def get_index():
    return Response({}, status=HTTPStatus.NO_CONTENT)


async def get_greeting(name):
    return Response({"welcome": name}, status=HTTPStatus.OK)
