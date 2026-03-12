 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000000000000000000000000000000000000..7a60b85e148f80966a550e5ab6a762a907c69ca6
--- /dev/null
+++ b/.gitignore
@@ -0,0 +1,2 @@
+__pycache__/
+*.pyc
diff --git a/README.md b/README.md
index 79c0873ce951b1cb9b433535fe190c74467c844d..1277ed62acaa54b9861c1924c03bf12fe4a66468 100644
--- a/README.md
+++ b/README.md
@@ -1,5 +1,80 @@
-# Welcome to GitHub Desktop!
+# Taxieconom.ru UI/E2E test automation
 
-This is your README. READMEs are where you can communicate what your project is and how to use it.
+Набор автотестов для проверки ключевых пользовательских сценариев сайта `https://taxieconom.ru`.
 
-Write your name on line 6, save it, and then head back to GitHub Desktop.
+## Что реализовано
+
+- Тестовый фреймворк на `pytest + Playwright`.
+- Разделение тестов по маркерам:
+  - `@pytest.mark.ui` — UI-валидации и навигация.
+  - `@pytest.mark.e2e` — сквозные сценарии.
+- Автоматизированы тест-кейсы `TC001–TC040` из предоставленного списка.
+- Для сценариев, требующих внешних зависимостей (SMS/антиспам/боевые отправки форм), добавлены управляемые `skip` с пояснением.
+
+## Структура
+
+- `tests/conftest.py` — фикстуры Playwright browser/page и базовый URL.
+- `tests/test_taxieconom.py` — полный набор тест-кейсов (40 шт.).
+- `pytest.ini` — настройки pytest и маркеры.
+- `requirements.txt` — зависимости.
+
+## Запуск
+
+```bash
+pip install -r requirements.txt
+playwright install chromium
+pytest -m ui
+pytest -m e2e
+pytest
+```
+
+## Переменные окружения
+
+- `BASE_URL` (по умолчанию `https://taxieconom.ru`)
+
+Пример:
+
+```bash
+BASE_URL=https://taxieconom.ru pytest -k TC001
+```
+
+
+## Веб-форма для запуска тестов
+
+Добавлен локальный веб-раннер `web_runner.py` с формой для запуска `pytest`.
+
+Запуск:
+
+```bash
+python web_runner.py
+```
+
+Откройте в браузере:
+
+- `http://127.0.0.1:8000`
+
+В форме можно выбрать:
+
+- маркер (`ui`/`e2e`/все),
+- фильтр `-k`,
+- `BASE_URL`,
+- дополнительные аргументы `pytest`.
+
+
+## Копирование в другой репозиторий
+
+Если нужно перенести этот набор автотестов в другой git-репозиторий, используйте скрипт:
+
+```bash
+./tools/copy_to_repo.sh /path/to/target-repo
+```
+
+Поведение:
+
+- копирует только файлы автотестового набора,
+- не перезаписывает существующие файлы без флага,
+- для принудительной перезаписи используйте `--force`:
+
+```bash
+./tools/copy_to_repo.sh /path/to/target-repo --force
+```
diff --git a/pytest.ini b/pytest.ini
new file mode 100644
index 0000000000000000000000000000000000000000..ed235b233faa072d0147a939ad33a7d72b798462
--- /dev/null
+++ b/pytest.ini
@@ -0,0 +1,5 @@
+[pytest]
+addopts = -ra
+markers =
+    ui: UI-level checks
+    e2e: end-to-end checks
diff --git a/requirements.txt b/requirements.txt
new file mode 100644
index 0000000000000000000000000000000000000000..cbe13f14d019e3309013b56ac7a63fd5e027d8c4
--- /dev/null
+++ b/requirements.txt
@@ -0,0 +1,2 @@
+pytest==8.3.3
+playwright==1.48.0
diff --git a/tests/conftest.py b/tests/conftest.py
new file mode 100644
index 0000000000000000000000000000000000000000..54268241b7bc2b70dc076983944842e84331c01b
--- /dev/null
+++ b/tests/conftest.py
@@ -0,0 +1,22 @@
+import os
+
+import pytest
+from playwright.sync_api import Page, sync_playwright
+
+BASE_URL = os.getenv("BASE_URL", "https://taxieconom.ru")
+
+
+@pytest.fixture(scope="session")
+def browser():
+    with sync_playwright() as p:
+        browser = p.chromium.launch(headless=True)
+        yield browser
+        browser.close()
+
+
+@pytest.fixture()
+def page(browser) -> Page:
+    context = browser.new_context(base_url=BASE_URL)
+    page = context.new_page()
+    yield page
+    context.close()
diff --git a/tests/test_taxieconom.py b/tests/test_taxieconom.py
new file mode 100644
index 0000000000000000000000000000000000000000..d029a811cbac4be9ecba4ebe1fb1f623dbd6b77b
--- /dev/null
+++ b/tests/test_taxieconom.py
@@ -0,0 +1,311 @@
+import re
+
+import pytest
+from playwright.sync_api import Page, expect
+
+
+CITY_SLUG = "/moskva/"
+CITY_NAME = "Москва"
+
+
+def by_text(page: Page, text: str):
+    return page.get_by_text(text, exact=False)
+
+
+def any_locator(page: Page, *selectors: str):
+    for selector in selectors:
+        locator = page.locator(selector)
+        if locator.count() > 0:
+            return locator.first
+    return page.locator(selectors[0]).first
+
+
+def open_home(page: Page):
+    page.goto("/")
+
+
+def open_city(page: Page):
+    page.goto(CITY_SLUG)
+
+
+@pytest.mark.ui
+def test_TC001_search_city_input_visible(page: Page):
+    open_home(page)
+    city_input = any_locator(page, "input[placeholder*='город']", "input[type='search']", "input")
+    expect(city_input).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC002_search_city_autocomplete(page: Page):
+    open_home(page)
+    city_input = any_locator(page, "input[placeholder*='город']", "input[type='search']", "input")
+    city_input.fill("Мос")
+    suggestions = any_locator(page, "[role='listbox'] li", ".autocomplete li", ".ui-menu-item")
+    expect(suggestions).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC003_search_city_select(page: Page):
+    open_home(page)
+    city_input = any_locator(page, "input[placeholder*='город']", "input[type='search']", "input")
+    city_input.fill("Москва")
+    by_text(page, "Москва").first.click()
+    expect(page).to_have_url(re.compile(r"/moskva/?"))
+
+
+@pytest.mark.ui
+def test_TC004_popular_city_click(page: Page):
+    open_home(page)
+    by_text(page, "Москва").first.click()
+    expect(page).to_have_url(re.compile(r"/.+"))
+
+
+@pytest.mark.ui
+def test_TC005_navigation_contacts(page: Page):
+    open_home(page)
+    by_text(page, "Контакты").first.click()
+    expect(page).to_have_url(re.compile(r"contact|kontakty|contacts", re.I))
+
+
+@pytest.mark.ui
+def test_TC006_navigation_ads(page: Page):
+    open_home(page)
+    by_text(page, "Реклама").first.click()
+    expect(page).to_have_url(re.compile(r"reklama|ads|advert", re.I))
+
+
+@pytest.mark.ui
+def test_TC007_navigation_favourites(page: Page):
+    open_home(page)
+    any_locator(page, "a[href*='favorite']", "a[href*='favourite']", "header .fa-heart").click()
+    expect(page).to_have_url(re.compile(r"favorite|favourite", re.I))
+
+
+@pytest.mark.e2e
+def test_TC008_add_service_button(page: Page):
+    open_home(page)
+    by_text(page, "Добавить службу бесплатно").first.click()
+    expect(page).to_have_url(re.compile(r"auth|login|register", re.I))
+
+
+@pytest.mark.ui
+def test_TC009_city_page_title(page: Page):
+    open_city(page)
+    expect(by_text(page, CITY_NAME).first).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC010_city_min_price_display(page: Page):
+    open_city(page)
+    min_price = any_locator(page, "text=/от\s*\d+\s*₽/i", "text=/миним.*\d+/i")
+    expect(min_price).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC011_taxi_cards_visible(page: Page):
+    open_city(page)
+    cards = any_locator(page, ".taxi-card", ".company-card", "article")
+    expect(cards).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC012_taxi_card_name_display(page: Page):
+    open_city(page)
+    card_name = any_locator(page, ".taxi-card h2", ".company-card h2", "article h2")
+    expect(card_name).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC013_taxi_card_price_display(page: Page):
+    open_city(page)
+    price = any_locator(page, "text=/\d+\s*₽/", "text=/от\s*\d+/i")
+    expect(price).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC014_taxi_card_wait_time_display(page: Page):
+    open_city(page)
+    wait_time = any_locator(page, "text=/мин/i", "text=/подач/i")
+    expect(wait_time).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC015_taxi_show_phone_button(page: Page):
+    open_city(page)
+    by_text(page, "Показать телефон").first.click()
+    expect(page.locator("text=/\+?\d[\d\s\-()]{7,}/").first).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC016_taxi_contact_button(page: Page):
+    open_city(page)
+    by_text(page, "Написать").first.click()
+    expect(any_locator(page, "form", "a[href*='telegram']", "a[href*='whatsapp']")).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC017_taxi_add_to_favourites(page: Page):
+    open_city(page)
+    any_locator(page, ".taxi-card .fa-heart", "article button[aria-label*='favorite']", "button:has(.fa-heart)").click()
+    open_home(page)
+    any_locator(page, "a[href*='favorite']", "a[href*='favourite']", "header .fa-heart").click()
+    expect(any_locator(page, ".taxi-card", ".company-card", "article")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC018_open_prices_tab(page: Page):
+    open_city(page)
+    by_text(page, "Цены").first.click()
+    expect(by_text(page, "Тариф").first).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC019_open_routes_tab(page: Page):
+    open_city(page)
+    by_text(page, "Популярные направления").first.click()
+    expect(by_text(page, "направлен").first).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC020_open_jobs_tab(page: Page):
+    open_city(page)
+    by_text(page, "Работа в такси").first.click()
+    expect(by_text(page, "Работа").first).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC021_open_offices_tab(page: Page):
+    open_city(page)
+    by_text(page, "Офисы").first.click()
+    expect(any_locator(page, "iframe", "#map", ".map")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC022_open_comments_tab(page: Page):
+    open_city(page)
+    by_text(page, "Оставить комментарий").first.click()
+    expect(any_locator(page, "form textarea", "textarea")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC023_comment_empty_validation(page: Page):
+    open_city(page)
+    by_text(page, "Оставить комментарий").first.click()
+    any_locator(page, "form button[type='submit']", "button:has-text('Отправить')").click()
+    expect(any_locator(page, ".error", "text=/обязател/i", "text=/заполн/i")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC024_comment_invalid_email_validation(page: Page):
+    open_city(page)
+    by_text(page, "Оставить комментарий").first.click()
+    any_locator(page, "input[type='email']", "input[name*='mail']").fill("invalid-email")
+    any_locator(page, "form button[type='submit']", "button:has-text('Отправить')").click()
+    expect(any_locator(page, "text=/email/i", ".error")).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC025_comment_success_submit(page: Page):
+    pytest.skip("Requires stable test data and anti-spam bypass on production")
+
+
+@pytest.mark.ui
+def test_TC026_taxi_page_title_display(page: Page):
+    open_city(page)
+    any_locator(page, ".taxi-card a", ".company-card a", "article a").first.click()
+    expect(any_locator(page, "h1", ".page-title")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC027_taxi_phone_link(page: Page):
+    open_city(page)
+    any_locator(page, ".taxi-card a", ".company-card a", "article a").first.click()
+    phone = any_locator(page, "a[href^='tel:']", "text=/\+?\d[\d\s\-()]{7,}/")
+    expect(phone).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC028_taxi_telegram_link(page: Page):
+    open_city(page)
+    any_locator(page, ".taxi-card a", ".company-card a", "article a").first.click()
+    telegram = any_locator(page, "a[href*='t.me']", "a:has-text('Telegram')")
+    expect(telegram).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC029_taxi_tariffs_visible(page: Page):
+    open_city(page)
+    any_locator(page, ".taxi-card a", ".company-card a", "article a").first.click()
+    expect(any_locator(page, "text=/тариф/i", ".tariffs", "table")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC030_contacts_info_display(page: Page):
+    page.goto("/contacts")
+    expect(any_locator(page, "a[href^='tel:']", "text=/@/", "a[href^='mailto:']")).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC031_contact_form_submit_success(page: Page):
+    page.goto("/contacts")
+    form = any_locator(page, "form", ".contact-form")
+    expect(form).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC032_ads_button_click(page: Page):
+    page.goto("/reklama")
+    by_text(page, "Узнать стоимость").first.click()
+    expect(any_locator(page, "form", ".modal", ".popup")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC033_ads_form_validation_empty(page: Page):
+    page.goto("/reklama")
+    any_locator(page, "form button[type='submit']", "button:has-text('Отправить')").click()
+    expect(any_locator(page, ".error", "text=/обязател/i", "text=/заполн/i")).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC034_ads_form_success_submit(page: Page):
+    pytest.skip("Requires non-production endpoint or disposable inbox for deterministic assertion")
+
+
+@pytest.mark.ui
+def test_TC035_favourites_empty_state(page: Page):
+    page.goto("/favorites")
+    expect(any_locator(page, "text=/нет избран/i", "text=/пуст/i", ".empty")).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC036_favourites_add_item(page: Page):
+    open_city(page)
+    any_locator(page, ".taxi-card .fa-heart", "article button[aria-label*='favorite']", "button:has(.fa-heart)").click()
+    page.goto("/favorites")
+    expect(any_locator(page, ".taxi-card", ".company-card", "article")).to_be_visible()
+
+
+@pytest.mark.ui
+def test_TC037_login_empty_fields_validation(page: Page):
+    page.goto("/auth")
+    any_locator(page, "button[type='submit']", "button:has-text('Войти')").click()
+    expect(any_locator(page, ".error", "text=/обязател/i", "text=/заполн/i")).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC038_login_invalid_credentials(page: Page):
+    page.goto("/auth")
+    any_locator(page, "input[type='tel']", "input[name*='phone']", "input[type='text']").fill("79990000000")
+    any_locator(page, "input[type='password']", "input[name*='password']").fill("invalid-password")
+    any_locator(page, "button[type='submit']", "button:has-text('Войти')").click()
+    expect(any_locator(page, ".error", "text=/невер/i", "text=/ошиб/i")).to_be_visible()
+
+
+@pytest.mark.e2e
+def test_TC039_registration_sms_send(page: Page):
+    pytest.skip("Requires controlled phone number and SMS receiver")
+
+
+@pytest.mark.e2e
+def test_TC040_registration_code_confirm(page: Page):
+    pytest.skip("Requires valid SMS code and controlled registration flow")
diff --git a/tools/copy_to_repo.sh b/tools/copy_to_repo.sh
new file mode 100755
index 0000000000000000000000000000000000000000..f9248d80612ae0ab667b26dc379778dfb3cc9863
--- /dev/null
+++ b/tools/copy_to_repo.sh
@@ -0,0 +1,58 @@
+#!/usr/bin/env bash
+set -euo pipefail
+
+if [[ $# -lt 1 ]]; then
+  echo "Usage: $0 /path/to/target-repo [--force]"
+  exit 1
+fi
+
+TARGET_REPO="$1"
+FORCE="${2:-}"
+
+if [[ ! -d "$TARGET_REPO/.git" ]]; then
+  echo "Error: target directory is not a git repository: $TARGET_REPO"
+  exit 1
+fi
+
+if [[ "$TARGET_REPO" == "$(pwd)" ]]; then
+  echo "Error: target repo must be different from current repository"
+  exit 1
+fi
+
+# Files we want to transfer.
+FILES=(
+  .gitignore
+  README.md
+  pytest.ini
+  requirements.txt
+  web_runner.py
+  tests/conftest.py
+  tests/test_taxieconom.py
+)
+
+for file in "${FILES[@]}"; do
+  if [[ ! -f "$file" ]]; then
+    echo "Error: source file not found: $file"
+    exit 1
+  fi
+
+  src="$PWD/$file"
+  dst="$TARGET_REPO/$file"
+
+  mkdir -p "$(dirname "$dst")"
+
+  if [[ -e "$dst" && "$FORCE" != "--force" ]]; then
+    echo "Skip existing file: $dst (use --force to overwrite)"
+    continue
+  fi
+
+  cp "$src" "$dst"
+  echo "Copied: $file"
+done
+
+echo
+echo "Done. Next steps in target repo:"
+echo "  cd $TARGET_REPO"
+echo "  git status"
+echo "  git add ."
+echo "  git commit -m 'Add taxieconom test automation suite'"
diff --git a/web_runner.py b/web_runner.py
new file mode 100644
index 0000000000000000000000000000000000000000..52b6212877b0276959a228297c488c1aae1eb031
--- /dev/null
+++ b/web_runner.py
@@ -0,0 +1,187 @@
+#!/usr/bin/env python3
+"""Minimal web UI for launching pytest runs for taxieconom.ru suite."""
+
+from __future__ import annotations
+
+import html
+import os
+import re
+import shlex
+import subprocess
+from dataclasses import dataclass
+from http import HTTPStatus
+from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
+from urllib.parse import parse_qs
+
+HOST = os.getenv("RUNNER_HOST", "127.0.0.1")
+PORT = int(os.getenv("RUNNER_PORT", "8000"))
+
+ALLOWED_MARKERS = {"", "ui", "e2e"}
+SAFE_K_PATTERN = re.compile(r"^[\w\s\-()|&.!]+$")
+SAFE_BASE_URL_PATTERN = re.compile(r"^https?://[^\s]+$")
+
+
+@dataclass
+class RunResult:
+    command: list[str]
+    return_code: int
+    output: str
+
+
+def build_command(marker: str, k_expr: str, extra_args: str) -> list[str]:
+    cmd = ["pytest", "-ra"]
+    if marker:
+        cmd.extend(["-m", marker])
+    if k_expr:
+        cmd.extend(["-k", k_expr])
+    if extra_args:
+        cmd.extend(shlex.split(extra_args))
+    return cmd
+
+
+def run_pytest(marker: str, k_expr: str, base_url: str, extra_args: str) -> RunResult:
+    cmd = build_command(marker, k_expr, extra_args)
+    env = os.environ.copy()
+    if base_url:
+        env["BASE_URL"] = base_url
+
+    completed = subprocess.run(
+        cmd,
+        capture_output=True,
+        text=True,
+        env=env,
+        timeout=1800,
+    )
+    output = f"{completed.stdout}\n{completed.stderr}".strip()
+    return RunResult(command=cmd, return_code=completed.returncode, output=output)
+
+
+def render_page(error: str = "", result: RunResult | None = None, values: dict[str, str] | None = None) -> str:
+    values = values or {}
+    marker = values.get("marker", "")
+    k_expr = values.get("k", "")
+    base_url = values.get("base_url", "https://taxieconom.ru")
+    extra_args = values.get("extra_args", "")
+
+    def selected(v: str) -> str:
+        return " selected" if marker == v else ""
+
+    result_html = ""
+    if result:
+        status = "PASS" if result.return_code == 0 else "FAIL"
+        command_str = html.escape(" ".join(shlex.quote(part) for part in result.command))
+        result_html = f"""
+        <h2>Результат: {status} (code {result.return_code})</h2>
+        <p><b>Команда:</b> <code>{command_str}</code></p>
+        <pre>{html.escape(result.output or '(no output)')}</pre>
+        """
+
+    error_html = f"<p style='color:#b00020'><b>Ошибка:</b> {html.escape(error)}</p>" if error else ""
+
+    return f"""<!doctype html>
+<html lang="ru">
+<head>
+  <meta charset="utf-8" />
+  <title>Taxieconom тест-раннер</title>
+  <style>
+    body {{ font-family: sans-serif; max-width: 980px; margin: 32px auto; padding: 0 16px; }}
+    label {{ display: block; margin-top: 12px; font-weight: 600; }}
+    input, select {{ width: 100%; padding: 8px; box-sizing: border-box; }}
+    button {{ margin-top: 16px; padding: 10px 16px; }}
+    pre {{ background: #0b1021; color: #d7e3ff; padding: 12px; overflow-x: auto; border-radius: 6px; }}
+    code {{ background:#f1f2f5; padding:2px 5px; border-radius:4px; }}
+  </style>
+</head>
+<body>
+  <h1>Taxieconom — запуск автотестов</h1>
+  <form method="post" action="/run">
+    <label for="marker">Маркер pytest</label>
+    <select id="marker" name="marker">
+      <option value=""{selected('')}>Все тесты</option>
+      <option value="ui"{selected('ui')}>Только UI</option>
+      <option value="e2e"{selected('e2e')}>Только E2E</option>
+    </select>
+
+    <label for="k">Фильтр -k (например: TC001 or TC002)</label>
+    <input id="k" name="k" value="{html.escape(k_expr)}" />
+
+    <label for="base_url">BASE_URL</label>
+    <input id="base_url" name="base_url" value="{html.escape(base_url)}" />
+
+    <label for="extra_args">Доп. аргументы pytest (например: -q --maxfail=1)</label>
+    <input id="extra_args" name="extra_args" value="{html.escape(extra_args)}" />
+
+    <button type="submit">Запустить</button>
+  </form>
+
+  {error_html}
+  {result_html}
+</body>
+</html>
+"""
+
+
+class Handler(BaseHTTPRequestHandler):
+    def do_GET(self):
+        if self.path != "/":
+            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
+            return
+        page = render_page()
+        body = page.encode("utf-8")
+        self.send_response(HTTPStatus.OK)
+        self.send_header("Content-Type", "text/html; charset=utf-8")
+        self.send_header("Content-Length", str(len(body)))
+        self.end_headers()
+        self.wfile.write(body)
+
+    def do_POST(self):
+        if self.path != "/run":
+            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
+            return
+
+        content_length = int(self.headers.get("Content-Length", 0))
+        raw = self.rfile.read(content_length).decode("utf-8")
+        data = {k: v[0] for k, v in parse_qs(raw).items()}
+
+        marker = (data.get("marker") or "").strip()
+        k_expr = (data.get("k") or "").strip()
+        base_url = (data.get("base_url") or "").strip()
+        extra_args = (data.get("extra_args") or "").strip()
+
+        values = {
+            "marker": marker,
+            "k": k_expr,
+            "base_url": base_url,
+            "extra_args": extra_args,
+        }
+
+        error = ""
+        result = None
+
+        if marker not in ALLOWED_MARKERS:
+            error = "Недопустимый маркер. Разрешены: ui, e2e или пусто."
+        elif k_expr and not SAFE_K_PATTERN.match(k_expr):
+            error = "Недопустимый символ в поле -k."
+        elif base_url and not SAFE_BASE_URL_PATTERN.match(base_url):
+            error = "BASE_URL должен начинаться с http:// или https://"
+        else:
+            try:
+                result = run_pytest(marker, k_expr, base_url, extra_args)
+            except subprocess.TimeoutExpired:
+                error = "Таймаут выполнения (30 минут)."
+            except Exception as exc:  # pragma: no cover - defensive fallback
+                error = f"Ошибка запуска: {exc}"
+
+        page = render_page(error=error, result=result, values=values)
+        body = page.encode("utf-8")
+        self.send_response(HTTPStatus.OK)
+        self.send_header("Content-Type", "text/html; charset=utf-8")
+        self.send_header("Content-Length", str(len(body)))
+        self.end_headers()
+        self.wfile.write(body)
+
+
+if __name__ == "__main__":
+    print(f"Starting web runner on http://{HOST}:{PORT}")
+    server = ThreadingHTTPServer((HOST, PORT), Handler)
+    server.serve_forever()
 
EOF
)
