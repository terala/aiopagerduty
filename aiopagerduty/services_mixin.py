"""Services Mixin
"""

from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import Service
from typing import List


class ServicesMixin:
    """Services API Mixin
    """

    async def list_services(self: FetcherProtocol) -> List[Service]:
        """Fetch all services.

        Returns:
            Dict[str, Service]: Dictionary of all services, keyed by service id.
        """
        return await self.multi_fetch(Service, 'services', 'services')

    async def list_service(self: FetcherProtocol, service_id: str) -> Service:
        return await self.single_fetch(Service, f'services/{service_id}',
                                       'service')
