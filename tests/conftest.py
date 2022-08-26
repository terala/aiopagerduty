"""aiopagerduty module tests"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Dict, cast

import aiopagerduty
import pytest_asyncio
from aiopagerduty.models import UserInfo, UserRole
from assertpy import assert_that
from dotenv import load_dotenv
from pytest import fixture

API_KEY_NAME = "PAGERDUTY_API_KEY"

_logger = logging.getLogger(__name__)


@fixture(name="pd_api_key", scope="session")
def aiopagerduty_api_key() -> str:
    load_dotenv()
    api_key = os.getenv(API_KEY_NAME)
    return cast(str, api_key)


@fixture(scope="session", name="service_name")
def subject_service_name() -> str:
    return "Test Service"


# TODO: Check if event_loop from pytest_asyncio can be used.
@fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(name="pd", scope="session", autouse=True)
async def pd_client(pd_api_key: str) -> AsyncGenerator[aiopagerduty.Client, None]:
    client = aiopagerduty.Client(pd_api_key)
    async with client:
        pd: aiopagerduty.Client = client
        yield pd


@pytest_asyncio.fixture(name="pd_services", scope="session")
async def aiopagerduty_services(pd: aiopagerduty.Client) -> Dict[str, aiopagerduty.Service]:
    svcs = await pd.list_services()
    services: Dict[str, aiopagerduty.Service] = {}
    for s in svcs:
        services[s.name] = s
    return services


@pytest_asyncio.fixture(name="service", scope="session")
def subject_service(pd_services: Dict[str, aiopagerduty.Service],
                    service_name: str) -> aiopagerduty.Service:
    assert_that(pd_services).contains_key(service_name)
    svc = pd_services[service_name]
    assert_that(svc).is_not_none()
    return svc


@pytest_asyncio.fixture(name="user", scope="session")
async def pd_user(pd: aiopagerduty.Client) -> aiopagerduty.User:
    data = {
        "name": "Automation User",
        "email": "noreply@terala.net",
    }
    user_info = UserInfo(**data)
    user_info.role = UserRole.USER
    _logger.info(f"Creating user : {user_info.name} ...")
    user = await pd.create_user(user_info)

    yield user

    _logger.info(f"Deleting user: {user.name} ...")
    await pd.delete_user(user)
