"""Fetcher module that provides HTTP transport to PagerDuty API servers.
"""

import json
import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar

import aiohttp
from pydantic import BaseModel

_URL_PREFIX = 'https://api.pagerduty.com'

TBaseModel = TypeVar('TBaseModel', bound=BaseModel)

_logger = logging.getLogger(__name__)


class Error(aiohttp.ClientError):
    """PagerDuty error.
    """

    def __init__(self, message: Optional[str], status: int):
        """Constructor

        Args:
            message (str): Error message
            status (int): HTTP error code
        """
        aiohttp.ClientError.__init__(self)
        self._msg = message
        self._status = status

    def __str__(self) -> str:
        return f'Error: status: {self._status}, message: {self._msg}'

    @property
    def message(self) -> Optional[str]:
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

    async def fetch_json_result(self, url: str) -> Dict[str, Any]:
        u = f'{_URL_PREFIX}/{url}'
        async with self._session.get(u) as resp:
            data: str = await resp.text()
            if resp.status != HTTPStatus.OK:
                _logger.error('Error posting', extra={
                              'message': resp.reason,
                              'status': resp.status,
                              })
                raise Error(resp.reason, resp.status)
            obj: Dict[str, Any] = json.loads(data)
            return obj

    async def post_json_result(self, url: str,
                               data: Dict[str, Any]) -> Dict[str, Any]:
        u = f'{_URL_PREFIX}/{url}'
        async with self._session.post(u, json=data) as resp:
            resp_data: str = await resp.text()
            if resp.status != HTTPStatus.CREATED:
                _logger.error('Error posting', extra={
                              'message': resp.reason,
                              'status': resp.status,
                              })
                raise Error(resp.reason, resp.status)
            obj: Dict[str, Any] = json.loads(resp_data)
            return obj

    async def put_json_result(self, url: str,
                              data: Dict[str, Any]) -> Dict[str, Any]:
        u = f'{_URL_PREFIX}/{url}'
        async with self._session.put(u, json=data) as resp:
            resp_data: str = await resp.text()
            if resp.status != HTTPStatus.OK:
                _logger.error('Error posting', extra={
                    'message': resp.reason,
                    'status': resp.status,
                })
                raise Error(resp.reason, resp.status)
            obj: Dict[str, Any] = json.loads(resp_data)
            return obj

    async def delete(self, url: str, expected_status: HTTPStatus) -> None:
        u = f'{_URL_PREFIX}/{url}'
        async with self._session.delete(u) as resp:
            if resp.status != expected_status:
                _logger.error('Error posting', extra={
                              'message': resp.reason,
                              'status': resp.status,
                              })
                raise Error(resp.reason, resp.status)

    async def multi_fetch(self, model_type: Type[TBaseModel], url_part: str,
                          items_name: str) -> List[TBaseModel]:
        """Fetch a list of type paging if needed.

        Args:
            model_type (Type[TBaseModel]): Class of the return type
            url_part (str): Url part to make a query against
            items_name (str): Name of the items within the return json
                              that contains the items.

        Returns:
            List[TBaseModel]: List of items
        """
        return_val: List[TBaseModel] = []
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

    async def single_fetch(self, model_type: Type[TBaseModel], url: str,
                           item_name: str) -> TBaseModel:
        json_obj = await self.fetch_json_result(url)
        model = model_type(**json_obj[item_name])
        return model

    async def object_fetch(self, model_type: Type[TBaseModel],
                           url: str) -> TBaseModel:
        json_obj = await self.fetch_json_result(url)
        model = model_type(**json_obj)
        return model


class FetcherProtocol(Protocol):
    """Forward declarations for mypy
    """

    async def fetch_json_result(self, url: str) -> Dict[str, Any]: ...

    async def post_json_result(self, url: str,
                               data: Dict[str, Any]) -> Dict[str, Any]: ...

    async def put_json_result(self, url: str,
                              data: Dict[str, Any]) -> Dict[str, Any]: ...

    async def delete(self, url: str, expected_status: HTTPStatus) -> None: ...

    async def multi_fetch(self, model_type: Type[TBaseModel], url_part: str,
                          items_name: str) -> List[TBaseModel]: ...

    async def single_fetch(self, model_type: Type[TBaseModel], url: str,
                           item_name: str) -> TBaseModel: ...

    async def object_fetch(self, model_type: Type[TBaseModel],
                           url: str) -> TBaseModel: ...
