"""Tests for UMLSClient.get_atoms filtering parameters."""

import pytest

from nih_umls_mcp.umls_client import UMLSClient


class _Recorder:
    def __init__(self):
        self.endpoint = None
        self.params = None

    async def __call__(self, endpoint, params=None):
        self.endpoint = endpoint
        self.params = params
        return {"result": {"recordCount": 0, "results": []}}


@pytest.fixture
def client(monkeypatch):
    c = UMLSClient(api_key="dummy", version="current")
    recorder = _Recorder()
    monkeypatch.setattr(c, "_get", recorder)
    c._recorder = recorder
    return c


@pytest.mark.asyncio
async def test_get_atoms_defaults(client):
    await client.get_atoms("C0069805")
    assert client._recorder.endpoint == "content/current/CUI/C0069805/atoms"
    assert client._recorder.params == {"pageSize": 25, "pageNumber": 1}


@pytest.mark.asyncio
async def test_get_atoms_passes_sabs_and_ttys(client):
    await client.get_atoms(
        "C0069805",
        page_size=50,
        sabs="RXNORM",
        ttys="IN,SCD",
    )
    assert client._recorder.params == {
        "pageSize": 50,
        "pageNumber": 1,
        "sabs": "RXNORM",
        "ttys": "IN,SCD",
    }


@pytest.mark.asyncio
async def test_get_atoms_clamps_page_size_to_100(client):
    await client.get_atoms("C0069805", page_size=500)
    assert client._recorder.params["pageSize"] == 100


@pytest.mark.asyncio
async def test_get_atoms_omits_filters_when_none(client):
    await client.get_atoms("C0069805", sabs=None, ttys=None)
    assert "sabs" not in client._recorder.params
    assert "ttys" not in client._recorder.params
