# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server that exposes NIH UMLS (Unified Medical Language System) REST API and NIH VSAC (Value Set Authority Center) FHIR API to AI models. Python package using `mcp` SDK and `httpx` for HTTP calls. Requires a UMLS API key via `UMLS_API_KEY` environment variable (same key works for both APIs).

## Build & Development Commands

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies (pytest)
pip install -e ".[dev]"

# Run the MCP server
python -m nih_umls_mcp.server

# Run tests
pytest

# Run the test server script (verifies tool registration, no API key needed)
python examples/test_server.py

# Run the client example (requires UMLS_API_KEY)
python examples/client_example.py
```

## Architecture

Three-layer design:

- **`src/nih_umls_mcp/umls_client.py`** — `UMLSClient` class: async HTTP client wrapping the UMLS REST API (`https://uts-ws.nlm.nih.gov/rest`). Handles auth via API key query parameter. Methods: `search`, `get_cui`, `get_definitions`, `get_atoms`, `get_relations`, `get_source_concept`, `crosswalk`.

- **`src/nih_umls_mcp/vsac_client.py`** — `VSACClient` class: async HTTP client wrapping the VSAC FHIR API (`https://cts.nlm.nih.gov/fhir`). Handles auth via HTTP Basic Auth (username `apikey`, password is the UMLS key). Methods: `search_value_sets`, `get_value_set`, `expand_value_set`, `validate_code`, `lookup_code`, `subsumes`.

- **`src/nih_umls_mcp/server.py`** — MCP server using `mcp.server.Server`. Defines 12 tools (6 UMLS + 6 VSAC) via `@app.list_tools()` and `@app.call_tool()` decorators. Uses lazily-initialized global `UMLSClient` and `VSACClient` instances. Runs over stdio transport.

The server tool names don't map 1:1 to client method names (e.g., `get_concept` tool calls `client.get_cui()`, `crosswalk_codes` tool calls `client.crosswalk()`).

## Key Details

- Python >=3.10 required
- Build system: hatchling
- Entry point: `nih-umls-mcp` CLI command maps to `nih_umls_mcp.server:main`
- UMLS API rate limit: 20 requests/second per IP (no client-side rate limiting implemented)
- All API responses returned as JSON via `TextContent` objects
- Error handler filters sensitive keys (`apikey`, `api_key`, `password`, `token`) from error messages
