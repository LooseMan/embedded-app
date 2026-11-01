import json

import pytest


def _format_debug_value(value):
    if value is None or value == "":
        return "<empty>"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return str(value)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Print the last API interaction when an API test assertion fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    client = item.funcargs.get("client") or item.funcargs.get("mock_api_client")
    history = getattr(client, "last_interaction", None)
    if not history:
        return

    print("\n" + "=" * 72)
    print("ACTIONABLE DEBUGLOG: API INTERACTION FAILED")
    print(f"Target Test: {item.nodeid}")
    print("-" * 72)
    print(f"[REQUEST]  {history.get('method')} {history.get('url')}")
    print(f"[Headers]  {_format_debug_value(history.get('req_headers'))}")
    print(f"[Payload]  {_format_debug_value(history.get('req_body'))}")
    print("-" * 72)
    print(f"[RESPONSE] Status: {history.get('status_code', '<no response>')}")
    print(f"[Body]     {_format_debug_value(history.get('res_body'))}")
    if history.get("error"):
        print(f"[Error]    {history['error']}")
    print("=" * 72 + "\n")


def pytest_configure(config):
    """Show test names by default while preserving explicit -q/-v options."""
    if config.getoption("verbose") == 0:
        config.option.verbose = 2


@pytest.fixture
def anyio_backend():
    return "asyncio"
