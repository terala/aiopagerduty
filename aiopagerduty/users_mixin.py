"""Users Mixin
"""

import urllib
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import ResponsePlay, User, UserInfo


class UsersMixin:
    """Users API Mixin
    """

    async def list_user(self: FetcherProtocol, user_id: str) -> User:
        return await self.single_fetch(User, f'users/{user_id}', 'user')

    async def list_users(self: FetcherProtocol) -> List[User]:
        return await self.multi_fetch(User, 'users', 'users')

    async def delete_user(self: FetcherProtocol, user: User) -> None:
        url = f'users/{user.id}'
        await self.delete(url, HTTPStatus.NO_CONTENT)

    async def create_user(self: FetcherProtocol, user_info: UserInfo) -> User:
        url = 'users'
        data = {
            'user': user_info.dict(exclude_unset=True),
        }
        user_json = await self.post_json_result(url, data=data)
        user = User(**user_json['user'])
        return user

    async def update_user(self: FetcherProtocol, user: User) -> User:
        url = f'users/{user.id}'
        user_info = UserInfo(**user.dict(exclude_unset=True,
                                         exclude_none=True))
        data = {
            'user': user_info.dict(exclude_unset=True)
        }
        updated_json = await self.put_json_result(url, data=data)
        updated = User(**updated_json['user'])
        return updated

        # Response Plays

    async def list_response_plays(self: FetcherProtocol,
                                  query: Optional[str] = None,
                                  manual: bool = False) -> List[ResponsePlay]:
        query_params: Dict[str, Any] = {
            'filter_for_manual_run': manual,
        }
        if query is not None:
            query_params['query'] = query

        query_url = f'response_plays?filter_for_manual_run={urllib.parse.urlencode(query_params)}'
        return await self.multi_fetch(ResponsePlay, query_url,
                                      'response_plays')

    async def list_response_play(self: FetcherProtocol,
                                 reponseplay_id: str) -> ResponsePlay:
        query_url = f'response_plays/{reponseplay_id}'
        return await self.single_fetch(ResponsePlay, query_url,
                                       'response_play')
