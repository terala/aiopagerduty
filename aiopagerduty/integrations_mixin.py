"""Integrations Mixin
"""


from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import Integration, Service, Vendor


class IntegrationsMixin:
    """Integrations API
    """
    async def list_integration(self: FetcherProtocol, service_id: str,
                               integration_id: str) -> Integration:
        url = f'services/{service_id}/integrations/{integration_id}'
        return await self.single_fetch(Integration, url, 'integration')

    async def create_integration(self: FetcherProtocol, service: Service,
                                 vendor: Vendor, name: str) -> Integration:
        """Create an integration to a service
        Args:
            service (Service): Service to which this integration is added to.
            vendor (Vendor): Vendor of the integration
            name (str): Name of the integration

        Returns:
            Integration: Integration created
        """
        url = f'services/{service.id}/integrations'
        data = {
            'integration': {
                # 'type': 'event_transformer_api_inbound_integration',
                # 'type': 'generic_events_api_inbound_integration',
                'type': 'events_api_v2_inbound_integration',
                'name': name,
                'service': {
                    'id': service.id,
                    'type': service.type,
                },
                'vendor': {
                    'id': vendor.id,
                    'type': vendor.type,
                }
            }
        }
        intg = await self.post_json_result(url, data)
        model = Integration(**intg['integration'])
        return model
