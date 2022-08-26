import logging

import aiopagerduty
import pytest_asyncio

_logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(name="ep", scope="module")
async def escalation(pd: aiopagerduty.Client) -> aiopagerduty.EscalationPolicy:
    _logger.info("Module Setup(): Getting escalation policies")
    policies = await pd.list_escalation_policies()
    yield policies[0]
    _logger.info("Module Cleanup(): Cleaning up escalation policy")


async def test_create_service(ep: aiopagerduty.EscalationPolicy) -> None:
    _logger.info(f"Creating service with ep: {ep.name} ... ")


async def test_update_service(ep: aiopagerduty.EscalationPolicy) -> None:
    _logger.info("Updating service ...")


async def test_delete_service(ep: aiopagerduty.EscalationPolicy) -> None:
    _logger.info("Deleting service ...")
