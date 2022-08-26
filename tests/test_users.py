"""Users unit tests"""
import logging
import random

import aiopagerduty
from aiopagerduty.models import User
from assertpy import assert_that

from tests.helpers.utils import find_matching

_logger = logging.getLogger(__name__)


async def test_list_users(pd: aiopagerduty.Client) -> None:
    users = await pd.list_users()
    assert_that(users).is_not_none()
    assert_that(users).is_not_empty()


async def test_user_creation(pd: aiopagerduty.Client, user: User) -> None:
    _logger.info("user", extra={"user_name": user.name, "id": user.id, })
    users = await pd.list_users()
    tuser = find_matching(users, lambda u: u.name == user.name)
    assert_that(tuser).is_not_none()
    assert_that(tuser.name).is_equal_to(user.name)


async def test_user_update(pd: aiopagerduty.Client, user: User) -> None:
    expected = f"Random description # {random.randint(1000, 9999)}"
    user.description = expected

    nuser = await pd.update_user(user)
    assert_that(nuser).is_not_none()
    assert_that(nuser.description).is_equal_to(expected)
