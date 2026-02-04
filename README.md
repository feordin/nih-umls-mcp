# NIH UMLS MCP Server

An MCP (Model Context Protocol) server that provides access to the NIH UMLS (Unified Medical Language System) API. This server enables AI models to search medical terminology, look up concept definitions, explore relationships between medical concepts, and map codes between different medical coding systems.

## Overview

The Unified Medical Language System (UMLS) integrates biomedical terminology from many sources and provides a mapping structure among these vocabularies. It includes over 200 source vocabularies and classification systems, containing millions of names for medical concepts.

This MCP server exposes the UMLS REST API functionality through standardized MCP tools, making it easy for AI assistants to:
- Search for medical concepts and terminology
- Get detailed concept information and definitions
- Explore relationships between concepts (parent/child hierarchies)
- Map codes between different medical coding systems (e.g., ICD-10 ↔ SNOMED CT)
- Look up specific codes from vocabularies like ICD-10, SNOMED, RxNorm, LOINC, etc.

## Prerequisites

1. **UMLS API Key**: You need a UMLS API key to use this server. To obtain one:
   - Visit https://uts.nlm.nih.gov/uts/signup-login
   - Create an account or sign in
   - Go to "My Profile" and generate an API key
   - The key is free for users who agree to the UMLS license terms

## Installation

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/feordin/nih-umls-mcp.git
cd nih-umls-mcp

# Install the package
pip install -e .
```

### Option 2: Install with uv (recommended for MCP usage)

```bash
# Using uvx (no installation needed)
uvx nih-umls-mcp
```

## Configuration

The server requires your UMLS API key to be set as an environment variable:

```bash
export UMLS_API_KEY="your-api-key-here"
```

### Configuring with Claude Desktop

To use this server with Claude Desktop, add the following to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

Or if using uvx:

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

## Available Tools

The server provides the following MCP tools:

### 1. `search_umls`
Search for medical concepts, terms, or codes in the UMLS.

**Parameters:**
- `query` (string, required): Search term, medical concept, or code
- `search_type` (string, optional): Type of search - "exact", "words" (default), "leftTruncation", "rightTruncation", "normalizedString", "approximate"
- `page_size` (integer, optional): Number of results (1-25, default: 10)

**Example:**
```
Search for "diabetes mellitus" to find relevant concepts
```

### 2. `get_concept`
Get detailed information about a specific UMLS concept using its CUI (Concept Unique Identifier).

**Parameters:**
- `cui` (string, required): Concept Unique Identifier (e.g., "C0009044")

**Example:**
```
Get details for concept C0009044 (Closed Fracture)
```

### 3. `get_definitions`
Get all definitions for a concept from various medical vocabularies.

**Parameters:**
- `cui` (string, required): Concept Unique Identifier

**Example:**
```
Get definitions for diabetes mellitus concept
```

### 4. `get_concept_relations`
Get relationships between concepts (parent concepts, child concepts, related terms).

**Parameters:**
- `cui` (string, required): Concept Unique Identifier
- `page_size` (integer, optional): Number of results (1-25, default: 10)

**Example:**
```
Get parent and child concepts for diabetes mellitus
```

### 5. `crosswalk_codes`
Map a medical code from one coding system to equivalent codes in other systems.

**Parameters:**
- `source` (string, required): Source vocabulary (e.g., "ICD10CM", "SNOMEDCT_US", "RXNORM", "LOINC")
- `code` (string, required): The code to map
- `target_source` (string, optional): Specific target vocabulary to filter results
- `page_size` (integer, optional): Number of results (1-25, default: 10)

**Common vocabulary abbreviations:**
- `ICD10CM` - ICD-10 Clinical Modification
- `ICD9CM` - ICD-9 Clinical Modification
- `SNOMEDCT_US` - SNOMED CT US Edition
- `RXNORM` - RxNorm (medications)
- `LOINC` - Logical Observation Identifiers Names and Codes
- `CPT` - Current Procedural Terminology
- `HCPCS` - Healthcare Common Procedure Coding System
- `ICD10PCS` - ICD-10 Procedure Coding System
- `NDC` - National Drug Code

**Example:**
```
Map ICD-10 code E11.9 (Type 2 diabetes without complications) to SNOMED CT
```

### 6. `get_source_concept`
Get information about a specific code from a particular medical vocabulary.

**Parameters:**
- `source` (string, required): Source vocabulary abbreviation
- `code` (string, required): The code in that vocabulary

**Example:**
```
Get information about ICD-10 code E11.9
```

## Usage Examples

### Example 1: Finding a Medical Concept
```
User: "What is the UMLS concept for Type 2 Diabetes?"

AI uses search_umls:
- query: "Type 2 Diabetes Mellitus"
- search_type: "words"

Returns CUI C0011860 with name "Diabetes Mellitus, Non-Insulin-Dependent"
```

### Example 2: Code Mapping
```
User: "What is the SNOMED code for ICD-10 code E11.9?"

AI uses crosswalk_codes:
- source: "ICD10CM"
- code: "E11.9"
- target_source: "SNOMEDCT_US"

Returns SNOMED code 44054006 and other equivalent codes
```

### Example 3: Understanding Relationships
```
User: "What are the subtypes of diabetes?"

AI first uses search_umls to find diabetes CUI, then uses get_concept_relations
to explore child concepts and related terms.
```

## Development

### Running Tests
```bash
pip install -e ".[dev]"
pytest
```

### Project Structure
```
nih-umls-mcp/
├── src/
│   └── nih_umls_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server implementation
│       └── umls_client.py     # UMLS API client
├── pyproject.toml
└── README.md
```

## API Rate Limits

The UMLS API has rate limits:
- Maximum 20 requests per second per IP address
- The server doesn't currently implement rate limiting, so be mindful of usage patterns

## Troubleshooting

### "UMLS_API_KEY environment variable is required"
- Ensure you've set the `UMLS_API_KEY` environment variable
- Check that the key is valid by testing it at https://documentation.uts.nlm.nih.gov/umls-api-interactive.html

### HTTP 401 Unauthorized
- Your API key may be invalid or expired
- Regenerate your API key from your UTS profile

### HTTP 404 Not Found
- The CUI or code you're looking up doesn't exist in the UMLS
- Check the spelling and format of identifiers

## Resources

- [UMLS REST API Documentation](https://documentation.uts.nlm.nih.gov/rest/home.html)
- [UMLS Metathesaurus Browser](https://uts.nlm.nih.gov/uts/umls/home)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [UMLS License Information](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
