
from pathlib import Path

import pytest


ARTIFACTS_DIR = Path(__file__).parent / "test-results"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": "http://127.0.0.1:8000",
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def capture_failure_diagnostics(request, page):
    yield

    report = getattr(request.node, "rep_call", None)

    if report is None or not report.failed:
        return

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(
        char if char.isalnum() or char in "-_" else "_"
        for char in request.node.nodeid
    )

    screenshot_path = ARTIFACTS_DIR / f"{safe_name}.png"
    html_path = ARTIFACTS_DIR / f"{safe_name}.html"

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"\nСкриншот сохранён: {screenshot_path}")
    except Exception as exc:
        print(f"\nНе удалось сохранить скриншот: {exc}")

    try:
        html_path.write_text(page.content(), encoding="utf-8")
        print(f"HTML сохранён: {html_path}")
    except Exception as exc:
        print(f"\nНе удалось сохранить HTML: {exc}")
