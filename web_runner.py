#!/usr/bin/env python3
"""Minimal web UI for launching pytest runs for taxieconom.ru suite."""

from __future__ import annotations

import html
import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

HOST = os.getenv("RUNNER_HOST", "127.0.0.1")
PORT = int(os.getenv("RUNNER_PORT", "8000"))
TESTS_FILE = Path("tests/test_taxieconom.py")

ALLOWED_MARKERS = {"", "ui", "e2e"}
SAFE_K_PATTERN = re.compile(r"^[\w\s\-()|&.!]+$")
SAFE_BASE_URL_PATTERN = re.compile(r"^https?://[^\s]+$")
SAFE_TEST_ID_PATTERN = re.compile(r"^TC\d{3}$")
TEST_ID_PATTERN = re.compile(r"def\s+test_(TC\d{3})_[\w_]+\s*\(")


@dataclass
class RunResult:
    command: list[str]
    return_code: int
    output: str


def discover_test_ids() -> list[str]:
    if not TESTS_FILE.exists():
        return []
    content = TESTS_FILE.read_text(encoding="utf-8")
    ids = sorted(set(TEST_ID_PATTERN.findall(content)))
    return ids


def build_command(marker: str, k_expr: str, extra_args: str) -> list[str]:
    cmd = ["pytest", "-ra"]
    if marker:
        cmd.extend(["-m", marker])
    if k_expr:
        cmd.extend(["-k", k_expr])
    if extra_args:
        cmd.extend(shlex.split(extra_args))
    return cmd


def run_pytest(marker: str, k_expr: str, base_url: str, extra_args: str) -> RunResult:
    cmd = build_command(marker, k_expr, extra_args)
    env = os.environ.copy()
    if base_url:
        env["BASE_URL"] = base_url

    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=1800,
    )
    output = f"{completed.stdout}\n{completed.stderr}".strip()
    return RunResult(command=cmd, return_code=completed.returncode, output=output)


def render_page(
    error: str = "",
    result: RunResult | None = None,
    values: dict[str, str] | None = None,
    test_ids: list[str] | None = None,
) -> str:
    values = values or {}
    test_ids = test_ids or []
    marker = values.get("marker", "")
    k_expr = values.get("k", "")
    selected_test_id = values.get("test_id", "")
    base_url = values.get("base_url", "https://taxieconom.ru")
    extra_args = values.get("extra_args", "")

    def selected(v: str) -> str:
        return " selected" if marker == v else ""

    test_options = ['<option value="">Не выбрано (использовать только -k)</option>']
    for test_id in test_ids:
        sel = " selected" if selected_test_id == test_id else ""
        test_options.append(f'<option value="{test_id}"{sel}>{test_id}</option>')

    result_html = ""
    if result:
        status = "PASS" if result.return_code == 0 else "FAIL"
        command_str = html.escape(" ".join(shlex.quote(part) for part in result.command))
        result_html = f"""
        <h2>Результат: {status} (code {result.return_code})</h2>
        <p><b>Команда:</b> <code>{command_str}</code></p>
        <pre>{html.escape(result.output or '(no output)')}</pre>
        """

    error_html = f"<p style='color:#b00020'><b>Ошибка:</b> {html.escape(error)}</p>" if error else ""

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Taxieconom тест-раннер</title>
  <style>
    body {{ font-family: sans-serif; max-width: 980px; margin: 32px auto; padding: 0 16px; }}
    label {{ display: block; margin-top: 12px; font-weight: 600; }}
    input, select {{ width: 100%; padding: 8px; box-sizing: border-box; }}
    button {{ margin-top: 16px; padding: 10px 16px; }}
    pre {{ background: #0b1021; color: #d7e3ff; padding: 12px; overflow-x: auto; border-radius: 6px; }}
    code {{ background:#f1f2f5; padding:2px 5px; border-radius:4px; }}
    .hint {{ color:#5d667a; font-size: 14px; margin: 4px 0 0; }}
  </style>
</head>
<body>
  <h1>Taxieconom — запуск автотестов</h1>
  <form method="post" action="/run">
    <label for="test_id">Тест-кейс (TCxxx)</label>
    <select id="test_id" name="test_id">
      {''.join(test_options)}
    </select>
    <p class="hint">Если выбран тест-кейс, он будет добавлен в выражение <code>-k</code>.</p>

    <label for="marker">Маркер pytest</label>
    <select id="marker" name="marker">
      <option value=""{selected('')}>Все тесты</option>
      <option value="ui"{selected('ui')}>Только UI</option>
      <option value="e2e"{selected('e2e')}>Только E2E</option>
    </select>

    <label for="k">Фильтр -k (например: taxi and not auth)</label>
    <input id="k" name="k" value="{html.escape(k_expr)}" />

    <label for="base_url">BASE_URL</label>
    <input id="base_url" name="base_url" value="{html.escape(base_url)}" />

    <label for="extra_args">Доп. аргументы pytest (например: -q --maxfail=1)</label>
    <input id="extra_args" name="extra_args" value="{html.escape(extra_args)}" />

    <button type="submit">Запустить</button>
  </form>

  {error_html}
  {result_html}
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        page = render_page(test_ids=discover_test_ids())
        body = page.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/run":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length).decode("utf-8")
        data = {k: v[0] for k, v in parse_qs(raw).items()}

        marker = (data.get("marker") or "").strip()
        k_expr = (data.get("k") or "").strip()
        test_id = (data.get("test_id") or "").strip().upper()
        base_url = (data.get("base_url") or "").strip()
        extra_args = (data.get("extra_args") or "").strip()

        if test_id:
            k_expr = f"{test_id} and ({k_expr})" if k_expr else test_id

        values = {
            "marker": marker,
            "k": k_expr,
            "test_id": test_id,
            "base_url": base_url,
            "extra_args": extra_args,
        }

        error = ""
        result = None

        available_test_ids = discover_test_ids()

        if marker not in ALLOWED_MARKERS:
            error = "Недопустимый маркер. Разрешены: ui, e2e или пусто."
        elif test_id and (not SAFE_TEST_ID_PATTERN.match(test_id) or test_id not in available_test_ids):
            error = "Недопустимый test_id. Выберите тест-кейс из списка."
        elif k_expr and not SAFE_K_PATTERN.match(k_expr):
            error = "Недопустимый символ в поле -k."
        elif base_url and not SAFE_BASE_URL_PATTERN.match(base_url):
            error = "BASE_URL должен начинаться с http:// или https://"
        else:
            try:
                result = run_pytest(marker, k_expr, base_url, extra_args)
            except subprocess.TimeoutExpired:
                error = "Таймаут выполнения (30 минут)."
            except Exception as exc:  # pragma: no cover - defensive fallback
                error = f"Ошибка запуска: {exc}"

        page = render_page(error=error, result=result, values=values, test_ids=available_test_ids)
        body = page.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Starting web runner on http://{HOST}:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.serve_forever()
