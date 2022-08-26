import logging

import pytest

_logger = logging.getLogger(__name__)


@pytest.fixture(name="ep", scope="module")
def escalation() -> str:
    _logger.info("Module Setup(): Getting escalation policy")
    yield "test_ep"
    _logger.info("Module Cleanup(): Cleaning up escalation policy")


def test_create_service(ep: str) -> None:
    _logger.info("Creating service ... ")


def test_update_service(ep: str) -> None:
    _logger.info("Updating service ...")


def test_delete_service(ep: str) -> None:
    _logger.info("Deleting service ...")
