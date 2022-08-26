"""aiopagerduty Client module
"""

from aiopagerduty.fetcher import Fetcher
from aiopagerduty.integrations_mixin import IntegrationsMixin
from aiopagerduty.prioritites_mixin import PrioritiesMixin
from aiopagerduty.serviceorchestration_mixin import ServiceOrchestrationsMixin
from aiopagerduty.services_mixin import ServicesMixin
from aiopagerduty.teams_mixin import TeamsMixin
from aiopagerduty.users_mixin import UsersMixin
from aiopagerduty.vendors_mixin import VendorsMixin


class Client(ServiceOrchestrationsMixin, VendorsMixin, PrioritiesMixin,
             TeamsMixin, ServicesMixin, UsersMixin, IntegrationsMixin,
             Fetcher):
    """aiopagerduty Client API
    """

    def __init__(self, api_key: str) -> None:
        super().__init__(api_key=api_key)
