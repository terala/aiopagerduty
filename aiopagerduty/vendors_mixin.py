"""Vendors Mixin
"""


from async_lru import alru_cache

from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import Vendor


class VendorsMixin:
    """Vendors API Mixin
    """
    @alru_cache(maxsize=5)
    async def list_vendors(self: FetcherProtocol) -> list[Vendor]:
        """List of vendors with integrations.
        This list is cached since there are more than 400 vendors defined in the system.
        """
        return await self.multi_fetch(Vendor, 'vendors', 'vendors')

    async def list_vendor(self: FetcherProtocol, vendor_id: str) -> Vendor:
        result = await self.fetch_json_result(f'vendors/{vendor_id}')
        return Vendor(**result)
