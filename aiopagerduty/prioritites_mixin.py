"""PrioritiesMixin
"""
from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import Priority

from typing import List


class PrioritiesMixin:

    async def list_priorities(self: FetcherProtocol) -> List[Priority]:
        query_url = 'priorities'
        return await self.multi_fetch(Priority, query_url, 'priorities')
