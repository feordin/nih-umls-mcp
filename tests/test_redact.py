"""Tests that the UMLS API key never appears in tool error output."""

import httpx
import pytest

from nih_umls_mcp import server
from nih_umls_mcp.umls_client import UMLSClient

KEY = "test-secret-key-1234"


def test_redact_query_param(monkeypatch):
    monkeypatch.setenv("UMLS_API_KEY", KEY)
    text = f"Client error '404 Not Found' for url 'https://uts-ws.nlm.nih.gov/rest/x?string=a&apiKey={KEY}'"
    assert server._redact(text) == (
        "Client error '404 Not Found' for url 'https://uts-ws.nlm.nih.gov/rest/x?string=a&apiKey=REDACTED'"
    )


def test_redact_bare_key(monkeypatch):
    monkeypatch.setenv("UMLS_API_KEY", KEY)
    assert server._redact(f"key is {KEY}") == "key is REDACTED"


def test_redact_without_env_key(monkeypatch):
    monkeypatch.delenv("UMLS_API_KEY", raising=False)
    assert server._redact("no secrets here") == "no secrets here"


@pytest.fixture
def failing_client(monkeypatch):
    """A UMLS client whose every request returns HTTP 404."""
    monkeypatch.setenv("UMLS_API_KEY", KEY)
    c = UMLSClient(api_key=KEY)
    c.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(404, request=request)))
    monkeypatch.setattr(server, "umls_client", c)
    return c


@pytest.mark.asyncio
@pytest.mark.parametrize("name, arguments", [
    ("search_umls", {"query": "Alzheimer disease"}),
    ("get_source_concept", {"source": "LOINC", "code": "2345-7"}),
    # CUI-shaped code takes the inner handler that adds a hint
    ("get_source_concept", {"source": "LOINC", "code": "C0002395"}),
])
async def test_tool_errors_do_not_leak_key(failing_client, name, arguments):
    result = await server.call_tool(name, arguments)
    text = result[0].text
    assert "404" in text
    assert KEY not in text
    assert "apiKey=REDACTED" in text
