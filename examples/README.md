# Examples

This directory contains example scripts demonstrating the NIH UMLS MCP server functionality.

## Files

### test_server.py
Basic tests to verify the MCP server is set up correctly. Does not require a UMLS API key.

```bash
python examples/test_server.py
```

### client_example.py
Demonstrates direct usage of the UMLS client (without MCP). Requires a valid UMLS API key.

```bash
export UMLS_API_KEY="your-api-key-here"
python examples/client_example.py
```

## Getting an API Key

To run examples that require a UMLS API key:

1. Visit https://uts.nlm.nih.gov/uts/signup-login
2. Sign up or log in
3. Go to "My Profile"
4. Generate an API key
5. Set the environment variable: `export UMLS_API_KEY="your-key-here"`
