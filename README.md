# TaxiEconom UI Test Automation

[![UI tests](https://github.com/Dzango988/taxi/actions/workflows/ui-tests.yml/badge.svg)](https://github.com/Dzango988/taxi/actions/workflows/ui-tests.yml)

Portfolio project with automated UI regression tests for **taxieconom.ru**.

The project demonstrates practical work with Python, pytest and Playwright: page navigation, stable locators, parametrization, positive and negative authorization scenarios, native form validation, protected-page checks and test grouping with pytest markers.

## What is covered

- public pages and navigation;
- representative city pages;
- service cards and breadcrumbs;
- favourites page;
- login form;
- successful authorization using credentials from environment variables;
- negative authorization scenarios: wrong password, unknown user, empty credentials;
- access control for a protected account page;
- registration and password recovery form structure;
- contact and advertising forms;
- native required-field validation;
- news page;
- footer legal links.

At the time of the latest local run, the suite contains **23 tests**.

## Tech stack

- Python 3.10+
- pytest
- Playwright
- pytest-playwright
- GitHub Actions

## Project structure

```text
.
├── .github/workflows/ui-tests.yml
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_public_pages.py
├── .env.example
├── .gitignore
├── CHECKLIST.md
├── pytest.ini
├── requirements.txt
└── README.md
```

## Installation

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Running tests

Full regression:

```bash
pytest -m regression --browser chromium -v
```

Smoke tests:

```bash
pytest -m smoke --browser chromium -v
```

Run with visible browser:

```bash
pytest --browser chromium --headed -v
```

Run only authorization tests:

```bash
pytest -m auth --browser chromium --headed -v
```

## Authorization credentials

Real credentials are **not stored in the repository**.

For the positive authorization test, set environment variables before running the tests.

Windows PowerShell:

```powershell
$env:TAXIECONOM_LOGIN="your_test_login@example.com"
$env:TAXIECONOM_PASSWORD="your_test_password"
pytest -m auth --browser chromium -v
```

macOS/Linux:

```bash
export TAXIECONOM_LOGIN="your_test_login@example.com"
export TAXIECONOM_PASSWORD="your_test_password"
pytest -m auth --browser chromium -v
```

If credentials are not provided, the positive login test is skipped safely.

## Test design notes

The suite intentionally avoids destructive actions on the production site. It does not submit real contact/advertising requests, register users via SMS, reset passwords, or modify account data.

Locators are selected to be resilient to duplicated or hidden responsive markup where possible. Tests focus on observable user behaviour rather than implementation details.

## CI

GitHub Actions runs public smoke tests on pushes and pull requests. The workflow does not require real account credentials.

## Checklist

A manual regression checklist used as the basis for the automated coverage is available in [CHECKLIST.md](CHECKLIST.md).

## Disclaimer

This is an independent educational/portfolio QA project. It is not an official project of taxieconom.ru.
