"""Service Orchestrations Mixin
"""
from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import (ObjectRef, ServiceOrchestration,
                                 ServiceOrchestrationStatus)


class ServiceOrchestrationsMixin:
    """ServiceOrchestration API Mixin
    """

    async def list_service_orchestration_status(
            self: FetcherProtocol,
            service_ref: ObjectRef) -> ServiceOrchestrationStatus:
        """Return the service orchestration status of a service.

        Args:
            service_ref (ObjectRef): Object reference to a service

        Returns:
            bool: True if orchestration is turned on for a service; False, otherwise.
        """
        url = f'event_orchestrations/services/{service_ref.id}/active'
        return await self.object_fetch(ServiceOrchestrationStatus, url)

    async def update_service_orchestration_status(
            self: FetcherProtocol, service_ref: ObjectRef,
            status: ServiceOrchestrationStatus) -> ServiceOrchestrationStatus:
        """Enable/disable service orchestration status for a service.
        Args:
            service_ref (ObjectRef): Object reference to the service
            status (ServiceOrchestrationStatus): Status to update

        Returns:
            bool: Updated status
        """
        url = f'event_orchestrations/services/{service_ref.id}/active'
        json = await self.put_json_result(url, status.dict())
        status_new = ServiceOrchestrationStatus(**json)
        return status_new

    async def list_service_orchestration(
            self: FetcherProtocol,
            service_ref: ObjectRef) -> ServiceOrchestration:
        """Get Service Orchestration rules defined for a service.

        Args:
            service_ref (ObjectRef): Service object reference.

        Returns:
            ServiceOrchestration: Orchestration rules defined for a service
        """
        url = f'event_orchestrations/services/{service_ref.id}'
        # return await self._object_fetch(ServiceOrchestration, url)
        return await self.single_fetch(ServiceOrchestration, url,
                                       'orchestration_path')
