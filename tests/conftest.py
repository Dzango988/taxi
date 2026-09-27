import os

import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "https://taxieconom.ru").rstrip("/")


@pytest.fixture(autouse=True)
def configure_page(page):
    page.set_default_timeout(15_000)
    page.set_default_navigation_timeout(30_000)
    return page
