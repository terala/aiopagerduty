"""Unit tests for Service Orchestration
"""
import json
from typing import Callable, TypeVar

import aiopagerduty
import pytest
from aiopagerduty.models import ServiceOrchestration
from assertpy import assert_that

T = TypeVar("T")
TArg = TypeVar("TArg")
TResult = TypeVar("TResult")


def find_matching(arr: list[T], pred_fn: Callable[[T], bool]) -> T | None:
    for x in arr:
        if pred_fn(x) is True:
            return x
    return None


def find_matching_or_throw(arr: list[T], pred_fn: Callable[[T], bool]) -> T:
    val: T | None = find_matching(arr, pred_fn)
    if val is None:
        raise LookupError()
    return val


def test_deserialize_empty_orchestration() -> None:
    json_text = """
        {
            "orchestration_path": {
                "catch_all": {
                    "actions": {}
                },
                "created_at": "2022-08-18T18:05:33Z",
                "created_by": null,
                "parent": {
                    "id": "PIRF4OU",
                    "self": "https://api.pagerduty.com/services/PIRF4OU",
                    "type": "service_reference"
                },
                "self": "https://api.pagerduty.com/event_orchestrations/services/PIRF4OU",
                "sets": [
                    {
                        "id": "start",
                        "rules": []
                    }
                ],
                "type": "service",
                "updated_at": "2022-08-18T18:05:33Z",
                "updated_by": null,
                "version": null
            }
        }
    """
    json_data = json.loads(json_text)
    orch = ServiceOrchestration(**json_data["orchestration_path"])
    assert_that(orch).is_not_none()


def test_deserialize_orchestration_with_two_sets() -> None:
    json_text = """
    {
        "orchestration_path": {
            "catch_all": {
                "actions": {
                    "severity": "info",
                    "suppress": true
                }
            },
            "created_at": "2022-06-24T21:50:39Z",
            "created_by": null,
            "parent": {
                "id": "P62L2FC",
                "self": "https://api.pagerduty.com/services/P62L2FC",
                "type": "service_reference"
            },
            "self": "https://api.pagerduty.com/event_orchestrations/services/P62L2FC",
            "sets": [
                {
                    "id": "start",
                    "rules": [
                        {
                            "actions": {
                                "route_to": "43754954",
                                "severity": "critical"
                            },
                            "conditions": [
                                {
                                    "expression": "event.custom_details.AWSAccountId matches '698789646528'"
                                },
                                {
                                    "expression": "event.custom_details.AWSAccountId matches '987345461176'"
                                }
                            ],
                            "id": "69a11a44",
                            "label": "Prod and Demo env"
                        }
                    ]
                },
                {
                    "id": "43754954",
                    "rules": [
                        {
                            "actions": {
                                "priority": "P1LAFKQ",
                                "severity": "critical"
                            },
                            "conditions": [
                                {
                                    "expression": "event.custom_details.AlarmName matches regex '^P2_*'"
                                }
                            ],
                            "id": "d109e587",
                            "label": null
                        }
                    ]
                }
            ],
            "type": "service",
            "updated_at": "2022-08-17T18:17:41Z",
            "updated_by": {
                "id": "P0XNIOX",
                "self": "https://api.pagerduty.com/users/P0XNIOX",
                "type": "user_reference"
            },
            "version": "iNIhdF5djxGICuYdu1vXb6LKSZoZ2HPY"
        }
    }
    """
    json_data = json.loads(json_text)
    orch = ServiceOrchestration(**json_data["orchestration_path"])
    assert_that(orch).is_not_none()


@pytest.mark.asyncio
@pytest.mark.parametrize("svc_name", ["Test Service"])
async def test_load_service_orchestrations(pd: aiopagerduty.Client,
                                           svc_name: str) -> None:
    # Find the service
    # svc_name = "Address Service"
    services = await pd.list_services()
    svc: aiopagerduty.Service = find_matching_or_throw(
        services, lambda s: s.name == svc_name)

    # Get the service orchestration for the service
    orch = await pd.list_service_orchestration(svc)
    assert_that(orch).is_not_none()
    assert_that(orch.parent.id).is_equal_to(svc.id)


@pytest.mark.asyncio
@pytest.mark.parametrize("svc_name,active", [
    ("Test Service", True)])
async def test_service_orchestration_status(pd: aiopagerduty.Client,
                                            pd_services: dict[str, aiopagerduty.Service],
                                            svc_name: str, active: bool) -> None:
    assert_that(pd_services).contains_key(svc_name)
    svc = pd_services[svc_name]
    assert_that(svc).is_not_none()
    status = await pd.list_service_orchestration_status(svc)
    assert_that(status).is_not_none()
    assert_that(status.active).is_equal_to(active)


async def test_deactivate_service_orchestration_status(
        pd: aiopagerduty.Client,
        service: aiopagerduty.Service,) -> None:

    svc = service

    async def update_and_test_status(status: aiopagerduty.ServiceOrchestrationStatus) -> None:
        status_new = await pd.update_service_orchestration_status(svc, status)
        assert_that(status_new).is_not_none()
        assert_that(status_new.active).is_equal_to(status.active)

        status_fetch = await pd.list_service_orchestration_status(svc)
        assert_that(status_fetch.active).is_equal_to(status.active)

    # deactivate
    status_deactive = aiopagerduty.ServiceOrchestrationStatus(active=False)
    await update_and_test_status(status_deactive)

    # Activate
    status_active = aiopagerduty.ServiceOrchestrationStatus(active=True)
    await update_and_test_status(status_active)
