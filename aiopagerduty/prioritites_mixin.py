"""PrioritiesMixin
"""
from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import Priority


class PrioritiesMixin:
    async def list_priorities(self: FetcherProtocol) -> list[Priority]:
        query_url = 'priorities'
        return await self.multi_fetch(Priority, query_url, 'priorities')
