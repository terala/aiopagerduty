"""Users unit tests"""
import aiopagerduty
from aiopagerduty.models import User
from assertpy import assert_that

from tests.helpers.utils import find_matching


async def test_list_users(pd: aiopagerduty.Client) -> None:
    users = await pd.list_users()
    assert_that(users).is_not_none()
    assert_that(users).is_not_empty()


async def test_user_creation(pd: aiopagerduty.Client, user: User) -> None:
    users = await pd.list_users()
    tuser = find_matching(users, lambda u: u == user.name)
    assert_that(tuser).is_not_none()
    assert_that(tuser.name).is_equal_to(user.name)
