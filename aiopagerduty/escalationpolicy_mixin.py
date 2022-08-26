"""Escalation Policy Mixin
"""

from typing import List

from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import EscalationPolicy


class EscalationPolicyMixin:
    """Escalation Policy API
    """

    async def list_escalation_policies(self: FetcherProtocol) -> List[EscalationPolicy]:
        url = "escalation_policies"
        return await self.multi_fetch(EscalationPolicy, url, "escalation_policies")

    async def list_escalation_policy(self: FetcherProtocol, ep_id: str) -> EscalationPolicy:
        url = f"escalation_policies/{ep_id}"
        return await self.single_fetch(EscalationPolicy, url, "escalation_policy")
