"""Fetcher module that provides HTTP transport to PagerDuty API servers.
"""

import json
from typing import Any, Protocol, TypeVar

import aiohttp
from pydantic import BaseModel

_URL_PREFIX = 'https://api.pagerduty.com'

TBaseModel = TypeVar('TBaseModel', bound=BaseModel)


class Error(aiohttp.ClientError):
    """PagerDuty error.
    """

    def __init__(self, message: str | None, status: int):
        """Constructor

        Args:
            message (str): Error message
            status (int): HTTP error code
        """
        aiohttp.ClientError.__init__(self)
        self._msg = message
        self._status = status

    @property
    def message(self) -> str | None:
        return self._msg

    @property
    def status(self) -> int:
        return self._status


class Fetcher:
    """Mixin to fetch json results from url.
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    # Async ContextManager support
    async def __aenter__(self) -> None:
        headers = {'Authorization': f'Token token={self._api_key}'}
        # Use max of 25 concurrent connections to limit PagerDuty
        # rate limiting issues.
        conn = aiohttp.TCPConnector(limit=25)
        self._session = aiohttp.ClientSession(headers=headers, connector=conn)
        # self._session = CachedSession(cache=SQLiteBackend(
        #     'pd.cache'), headers=headers, connector=conn)
        pass

    # Async ContextManager support
    async def __aexit__(self, *args: Any) -> None:
        await self._session.close()

    async def fetch_json_result(self, url: str) -> dict[str, Any]:
        u = f'{_URL_PREFIX}/{url}'
        async with self._session.get(u) as resp:
            data: str = await resp.text()
            if resp.status != 200:
                raise Error(resp.reason, resp.status)
            obj: dict[str, Any] = json.loads(data)
            return obj

    async def post_json_result(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        u = f'{_URL_PREFIX}/{url}'
        async with self._session.post(u, json=data) as resp:
            resp_data: str = await resp.text()
            if resp.status != 201:
                raise Error(resp.reason, resp.status)
            obj: dict[str, Any] = json.loads(resp_data)
            return obj

    async def put_json_result(self, url: str, data: dict[str, Any]) -> dict[str, Any]:
        u = f'{_URL_PREFIX}/{url}'
        async with self._session.put(u, json=data) as resp:
            resp_data: str = await resp.text()
            if resp.status != 200:
                raise Error(resp.reason, resp.status)
            obj: dict[str, Any] = json.loads(resp_data)
            return obj

    async def multi_fetch(self, model_type: type[TBaseModel],
                          url_part: str, items_name: str) -> list[TBaseModel]:
        """Fetch a list of type paging if needed.

        Args:
            model_type (type[TBaseModel]): Class of the return type
            url_part (str): Url part to make a query against
            items_name (str): Name of the items within the return json
                              that contains the items.

        Returns:
            list[TBaseModel]: List of items
        """
        return_val: list[TBaseModel] = []
        fetch: bool = True
        offset = 0
        limit = 100
        while fetch is True:  # pylint: disable=while-used
            url = f'{url_part}?offset={offset}&limit={limit}'
            result = await self.fetch_json_result(url)
            fetch = result['more']
            offset += len(result[items_name])
            for json_obj in result[items_name]:
                item = model_type(**json_obj)
                return_val.append(item)
        return return_val

    async def single_fetch(self, model_type: type[TBaseModel],
                           url: str, item_name: str) -> TBaseModel:
        json_obj = await self.fetch_json_result(url)
        model = model_type(**json_obj[item_name])
        return model

    async def object_fetch(self, model_type: type[TBaseModel],
                           url: str) -> TBaseModel:
        json_obj = await self.fetch_json_result(url)
        model = model_type(**json_obj)
        return model


class FetcherProtocol(Protocol):
    """Forward declarations for mypy
    """
    async def fetch_json_result(self, url: str) -> dict[str, Any]: ...

    async def post_json_result(
        self, url: str, data: dict[str, Any]) -> dict[str, Any]: ...

    async def put_json_result(
        self, url: str, data: dict[str, Any]) -> dict[str, Any]: ...

    async def multi_fetch(self, model_type: type[TBaseModel],
                          url_part: str, items_name: str) -> list[TBaseModel]: ...

    async def single_fetch(self, model_type: type[TBaseModel],
                           url: str, item_name: str) -> TBaseModel: ...

    async def object_fetch(self, model_type: type[TBaseModel],
                           url: str) -> TBaseModel: ...
