import os

import pytest
from playwright.sync_api import Page, expect


LOGIN_PATH = "/account/"
PROTECTED_PATH = "/account/add/"
INVALID_CREDENTIALS_MESSAGE = "Неверный логин или пароль."


def open_login(page: Page, base_url: str) -> None:
    response = page.goto(f"{base_url}{LOGIN_PATH}", wait_until="domcontentloaded")
    assert response is not None, "Нет HTTP-ответа страницы авторизации"
    assert response.status < 400, f"Страница авторизации вернула HTTP {response.status}"


def submit_login(page: Page, login: str, password: str) -> None:
    page.get_by_placeholder("E-mail или телефон").fill(login)
    page.get_by_placeholder("Пароль").fill(password)
    page.locator('input[name="auth"]').click()
    page.wait_for_load_state("domcontentloaded")


@pytest.fixture(scope="session")
def auth_credentials() -> tuple[str, str]:
    login = os.getenv("TAXIECONOM_LOGIN")
    password = os.getenv("TAXIECONOM_PASSWORD")
    if not login or not password:
        pytest.skip(
            "Для позитивного auth-теста задайте TAXIECONOM_LOGIN и TAXIECONOM_PASSWORD"
        )
    return login, password


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.auth
def test_login_with_valid_credentials_allows_protected_page(
    page: Page, base_url: str, auth_credentials: tuple[str, str]
):
    login, password = auth_credentials
    open_login(page, base_url)
    submit_login(page, login, password)

    expect(page.get_by_text(INVALID_CREDENTIALS_MESSAGE, exact=True)).not_to_be_visible()

    response = page.goto(f"{base_url}{PROTECTED_PATH}", wait_until="domcontentloaded")
    assert response is not None, "Нет HTTP-ответа защищённой страницы"
    assert response.status < 400, f"Защищённая страница вернула HTTP {response.status}"
    expect(page).not_to_have_url(f"{base_url}{LOGIN_PATH}")
    expect(page.get_by_placeholder("Пароль")).not_to_be_visible()


@pytest.mark.regression
@pytest.mark.auth
def test_login_with_wrong_password_shows_error(page: Page, base_url: str):
    open_login(page, base_url)
    submit_login(page, "qa.invalid@example.com", "DefinitelyWrongPassword_987654")

    expect(page).to_have_url(f"{base_url}{LOGIN_PATH}")
    expect(page.get_by_text(INVALID_CREDENTIALS_MESSAGE, exact=True)).to_be_visible()
    expect(page.get_by_placeholder("Пароль")).to_be_visible()


@pytest.mark.regression
@pytest.mark.auth
def test_login_with_unknown_user_shows_error(page: Page, base_url: str):
    open_login(page, base_url)
    submit_login(page, "qa.user.does.not.exist.987654@example.com", "WrongPassword_987654")

    expect(page).to_have_url(f"{base_url}{LOGIN_PATH}")
    expect(page.get_by_text(INVALID_CREDENTIALS_MESSAGE, exact=True)).to_be_visible()
    expect(page.get_by_placeholder("Пароль")).to_be_visible()


@pytest.mark.regression
@pytest.mark.auth
def test_login_with_empty_credentials_does_not_authorize(page: Page, base_url: str):
    open_login(page, base_url)
    page.locator('input[name="auth"]').click()
    page.wait_for_load_state("domcontentloaded")

    expect(page).to_have_url(f"{base_url}{LOGIN_PATH}")
    expect(page.get_by_placeholder("E-mail или телефон")).to_be_visible()
    expect(page.get_by_placeholder("Пароль")).to_be_visible()
