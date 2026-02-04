# Example Claude Desktop Configuration

This file shows how to configure the NIH UMLS MCP server with Claude Desktop.

## Configuration Location

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Example Configuration

```json
{
  "mcpServers": {
    "nih-umls": {
      "command": "python",
      "args": ["-m", "nih_umls_mcp.server"],
      "env": {
        "UMLS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Getting Your API Key

1. Visit https://uts.nlm.nih.gov/uts/signup-login
2. Sign up or log in
3. Go to "My Profile" 
4. Generate an API key
5. Replace "your-api-key-here" in the configuration with your actual key

## Alternative: Using uvx

If you want to use uvx instead of a local installation:

```json
{
  "mcpServers": {
    "nih-umls": {
      "command": "uvx",
      "args": ["nih-umls-mcp"],
      "env": {
        "UMLS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```
