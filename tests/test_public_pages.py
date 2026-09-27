import re

import pytest
from playwright.sync_api import Page, expect


def open_page(page: Page, base_url: str, path: str) -> None:
    response = page.goto(f"{base_url}{path}", wait_until="domcontentloaded")
    assert response is not None, f"Нет HTTP-ответа для {path}"
    assert response.status < 400, f"{path} вернул HTTP {response.status}"


@pytest.mark.smoke
@pytest.mark.regression
def test_homepage_opens(page: Page, base_url: str):
    open_page(page, base_url, "/")
    expect(page).to_have_title(re.compile(r"Такси Эконом|Такси эконом", re.I))
    expect(page.get_by_role("heading", name="Такси в городах России", exact=True)).to_be_visible()


@pytest.mark.smoke
@pytest.mark.regression
def test_main_navigation(page: Page, base_url: str):
    open_page(page, base_url, "/")
    for text, href in (
        ("Реклама", "/order/"),
        ("Контакты", "/contact/"),
        ("Добавить службу бесплатно", "/account/add/"),
    ):
        link = page.get_by_role("link", name=text, exact=True).first
        expect(link).to_be_visible()
        expect(link).to_have_attribute("href", href)


@pytest.mark.smoke
@pytest.mark.regression
def test_popular_city_link_opens_city_page(page: Page, base_url: str):
    open_page(page, base_url, "/")
    page.get_by_role("link", name="Москва", exact=True).first.click()
    expect(page).to_have_url(f"{base_url}/moscow/")
    expect(page.get_by_role("heading", name="Такси Москвы", exact=True)).to_be_visible()


@pytest.mark.regression
def test_city_search_accepts_query_and_shows_result(page: Page, base_url: str):
    open_page(page, base_url, "/")
    search = page.get_by_placeholder("Начните вводить название города").first
    expect(search).to_be_visible()
    search.fill("Пенза")
    result = page.get_by_role("link", name=re.compile("Пенза", re.I)).first
    expect(result).to_be_visible()
    expect(result).to_have_attribute("href", re.compile(r"/penza/?$"))


@pytest.mark.regression
@pytest.mark.parametrize(
    "name,path,heading_pattern",
    [
        ("Москва", "/moscow/", r"Моск"),
        ("Санкт-Петербург", "/saint-petersburg/", r"Санкт-Петербург"),
        ("Сочи", "/sochi/", r"Сочи"),
    ],
)
def test_representative_city_pages(page: Page, base_url: str, name: str, path: str, heading_pattern: str):
    open_page(page, base_url, path)
    expect(page.locator("h1:visible").first).to_contain_text(re.compile(heading_pattern, re.I))
    service_links = page.locator("a.js-service-click")
    assert service_links.count() > 0, f"На странице {name} нет карточек служб"
    phone_links = page.locator('a[href^="tel:"]')
    assert phone_links.count() > 0, f"На странице {name} нет телефонных ссылок"


@pytest.mark.smoke
@pytest.mark.regression
def test_city_service_card_opens_detail(page: Page, base_url: str):
    open_page(page, base_url, "/moscow/")
    service = page.locator("a.js-service-click").first
    expected_name = service.inner_text().strip()
    service.click()
    expect(page.locator("h1:visible").first).to_have_text(expected_name)
    expect(page.get_by_role("heading", name="Цены и тарифы", exact=True)).to_be_visible()
    expect(page.get_by_role("heading", name="Контакты и адрес офиса", exact=True)).to_be_visible()


@pytest.mark.regression
def test_service_detail_breadcrumbs_and_phone(page: Page, base_url: str):
    open_page(page, base_url, "/moscow/yarkiy-mir-moskva/")
    expect(page.get_by_role("link", name="Главная", exact=True)).to_have_attribute("href", "/")
    expect(page.get_by_role("link", name="Такси Москвы", exact=True)).to_have_attribute("href", "/moscow/")
    assert page.locator('a[href^="tel:"]:visible').count() > 0


@pytest.mark.regression
def test_empty_favourites_page(page: Page, base_url: str):
    page.context.clear_cookies()
    open_page(page, base_url, "/favourite/")
    expect(page.get_by_role("heading", name="Избранное", exact=True)).to_be_visible()


@pytest.mark.smoke
@pytest.mark.regression
def test_login_form(page: Page, base_url: str):
    open_page(page, base_url, "/account/")
    expect(page).to_have_title("Авторизация")
    expect(page.get_by_placeholder("E-mail или телефон")).to_be_visible()
    expect(page.get_by_placeholder("Пароль")).to_be_visible()
    expect(page.locator('input[name="auth"]')).to_be_visible()
    expect(page.get_by_role("link", name="Мне нужна регистрация").first).to_have_attribute(
        "href", "/account/registration/"
    )
    expect(page.get_by_role("link", name="Забыли пароль?")).to_have_attribute(
        "href", "/account/recover/"
    )


@pytest.mark.regression
def test_login_required_for_adding_service(page: Page, base_url: str):
    open_page(page, base_url, "/account/add/")
    expect(page).to_have_url(f"{base_url}/account/")
    expect(page.get_by_placeholder("Пароль")).to_be_visible()


@pytest.mark.regression
def test_registration_form_structure(page: Page, base_url: str):
    open_page(page, base_url, "/account/registration/")
    expect(page).to_have_title("Регистрация пользователя")
    expect(page.get_by_placeholder("Введите телефон")).to_be_attached()
    expect(page.get_by_placeholder("Код из СМС")).to_be_attached()
    expect(page.get_by_placeholder("Введите e-mail")).to_be_attached()
    for name in ("RULES", "EULA", "PRIVACY_POLICY", "POPD"):
        expect(page.locator(f'input[name="{name}"]')).to_be_attached()


@pytest.mark.regression
def test_password_recovery_form(page: Page, base_url: str):
    open_page(page, base_url, "/account/recover/")
    expect(page).to_have_title("Запрос пароля")
    expect(page.get_by_placeholder("Введите e-mail или телефон")).to_be_visible()
    expect(page.locator('input[type="submit"]')).to_have_value("Отправить")


@pytest.mark.smoke
@pytest.mark.regression
def test_contact_form_structure(page: Page, base_url: str):
    open_page(page, base_url, "/contact/")
    expect(page.get_by_role("heading", name="Контакты", exact=True)).to_be_visible()
    expect(page.get_by_placeholder("Введите имя").filter(visible=True).first).to_be_visible()
    expect(page.get_by_placeholder("Введите email").filter(visible=True).first).to_be_visible()
    expect(page.get_by_placeholder("Сообщение").filter(visible=True).first).to_be_visible()
    expect(page.get_by_role("button", name="Отправить", exact=True).filter(visible=True).first).to_be_visible()


@pytest.mark.regression
def test_contact_form_native_required_validation(page: Page, base_url: str):
    open_page(page, base_url, "/contact/")
    for placeholder in ("Введите имя", "Введите email", "Сообщение"):
        field = page.get_by_placeholder(placeholder).filter(visible=True).first
        expect(field).to_be_visible()
        assert field.evaluate("el => el.required") is True, f"Поле {placeholder!r} не является обязательным"


@pytest.mark.regression
def test_advertising_form_structure(page: Page, base_url: str):
    open_page(page, base_url, "/order/")
    fields = (
        page.get_by_placeholder("Введите e-mail").filter(visible=True).first,
        page.get_by_placeholder("Название вашего такси").filter(visible=True).first,
        page.get_by_placeholder("Ваш номер телефона").filter(visible=True).first,
    )
    for field in fields:
        expect(field).to_be_visible()
        assert field.evaluate("el => el.required") is True, "Поле рекламной формы должно быть обязательным"


@pytest.mark.smoke
@pytest.mark.regression
def test_news_page_has_articles(page: Page, base_url: str):
    open_page(page, base_url, "/news/")
    expect(page.get_by_role("heading", name="Новости", exact=True)).to_be_visible()
    article_links = page.locator('main a[href^="/news/"]')
    assert article_links.count() > 0, "На странице новостей нет ссылок на статьи"


@pytest.mark.regression
def test_footer_legal_links(page: Page, base_url: str):
    open_page(page, base_url, "/")
    expected = {
        "Оферта": "/offer/",
        "Политика конфиденциальности": "/links/",
        "О нас": "/about/",
        "Новости": "/news/",
    }
    for name, href in expected.items():
        expect(page.get_by_role("link", name=name, exact=True).last).to_have_attribute("href", href)
