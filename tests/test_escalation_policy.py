"""Unit tests for escalation policy"""

import aiopagerduty
import pytest
from assertpy import assert_that

from tests.helpers.utils import find_matching


async def test_list_escalation_policies(pd: aiopagerduty.Client) -> None:
    policies = await pd.list_escalation_policies()
    assert_that(policies).is_not_none()
    assert_that(policies).is_not_empty()


@pytest.mark.asyncio
@pytest.mark.parametrize("policy_name", ["Default"])
async def test_list_escalation_policy_exists(pd: aiopagerduty.Client,
                                             policy_name: str) -> None:
    policies = await pd.list_escalation_policies()
    policy = find_matching(policies, lambda p: p.name == policy_name)
    assert_that(policy).is_not_none()
    assert_that(policy.name).is_equal_to(policy_name)
