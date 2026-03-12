# Taxieconom.ru UI/E2E test automation

Набор автотестов для проверки ключевых пользовательских сценариев сайта `https://taxieconom.ru`.

## Что реализовано

- Тестовый фреймворк на `pytest + Playwright`.
- Разделение тестов по маркерам:
  - `@pytest.mark.ui` — UI-валидации и навигация.
  - `@pytest.mark.e2e` — сквозные сценарии.
- Автоматизированы тест-кейсы `TC001–TC040` из предоставленного списка.
- Для сценариев, требующих внешних зависимостей (SMS/антиспам/боевые отправки форм), добавлены управляемые `skip` с пояснением.

## Структура

- `tests/conftest.py` — фикстуры Playwright browser/page и базовый URL.
- `tests/test_taxieconom.py` — полный набор тест-кейсов (40 шт.).
- `pytest.ini` — настройки pytest и маркеры.
- `requirements.txt` — зависимости.
- `web_runner.py` — простой веб-интерфейс для запуска pytest.
- `tools/copy_to_repo.sh` — перенос тестового набора в другой репозиторий.

## Установка и запуск

```bash
pip install -r requirements.txt
playwright install chromium
pytest -m ui
pytest -m e2e
pytest
```

## Переменные окружения

- `BASE_URL` (по умолчанию `https://taxieconom.ru`)

Пример:

```bash
BASE_URL=https://taxieconom.ru pytest -k TC001
```

## Веб-форма для запуска тестов

Запуск:

```bash
python web_runner.py
```

Откройте в браузере:

- `http://127.0.0.1:8000`

В форме можно выбрать:

- маркер (`ui`/`e2e`/все),
- выбор конкретного тест-кейса `TCxxx` из выпадающего списка,
- фильтр `-k`,
- `BASE_URL`,
- дополнительные аргументы `pytest`.

## Копирование в другой репозиторий

```bash
./tools/copy_to_repo.sh /path/to/target-repo
```

Для перезаписи файлов:

```bash
./tools/copy_to_repo.sh /path/to/target-repo --force
```
