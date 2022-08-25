"""Users Mixin
"""

import urllib
from typing import Any, Dict, List, Optional

from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import ResponsePlay, User


class UsersMixin:
    """Users API Mixin
    """

    async def list_user(self: FetcherProtocol, user_id: str) -> User:
        return await self.single_fetch(User, f'users/{user_id}', 'user')

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
