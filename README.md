# NIH UMLS MCP Server

An MCP (Model Context Protocol) server that provides access to the NIH UMLS (Unified Medical Language System) API and the NIH VSAC (Value Set Authority Center) FHIR API. This server enables AI models to search medical terminology, look up concept definitions, explore relationships between medical concepts, map codes between different medical coding systems, and work with curated clinical value sets.

## Overview

The **Unified Medical Language System (UMLS)** integrates biomedical terminology from many sources and provides a mapping structure among these vocabularies. It includes over 200 source vocabularies and classification systems, containing millions of names for medical concepts.

The **Value Set Authority Center (VSAC)** is an NLM repository of curated value sets — collections of medical codes from standard code systems (SNOMED CT, ICD-10, LOINC, CPT, RxNorm, etc.) that define clinical concepts for electronic Clinical Quality Measures (eCQMs), C-CDA documents, and health IT standards.

This MCP server exposes both APIs through standardized MCP tools, making it easy for AI assistants to:
- Search for medical concepts and terminology
- Get detailed concept information and definitions
- Explore relationships between concepts (parent/child hierarchies)
- Map codes between different medical coding systems (e.g., ICD-10 ↔ SNOMED CT)
- Look up specific codes from vocabularies like ICD-10, SNOMED, RxNorm, LOINC, etc.
- Search and retrieve curated clinical value sets
- Expand value sets to get all member codes
- Validate whether a code belongs to a value set
- Test hierarchical subsumption relationships between codes

## Prerequisites

1. **UMLS API Key**: You need a UMLS API key to use this server (the same key works for both UMLS and VSAC). To obtain one:
   - Visit https://uts.nlm.nih.gov/uts/signup-login
   - Create an account or sign in
   - Go to "My Profile" and generate an API key
   - The key is free for users who agree to the UMLS license terms

## Installation

### Option 1: Install from PyPI

```bash
pip install nih-umls-mcp
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/feordin/nih-umls-mcp.git
cd nih-umls-mcp

# Install the package
pip install -e .
```

### Option 3: Install with uv (recommended for MCP usage)

```bash
# Using uvx (no installation needed)
uvx nih-umls-mcp
```

### Upgrading

```bash
# If installed with pip
pip install --upgrade nih-umls-mcp

# If installed with uv
uv tool upgrade nih-umls-mcp
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

### UMLS Tools

#### 1. `search_umls`
Search for medical concepts, terms, or codes in the UMLS.

**Parameters:**
- `query` (string, required): Search term, medical concept, or code
- `search_type` (string, optional): Type of search - "exact", "words" (default), "leftTruncation", "rightTruncation", "normalizedString", "approximate"
- `page_size` (integer, optional): Number of results (1-25, default: 10)

**Example:**
```
Search for "diabetes mellitus" to find relevant concepts
```

#### 2. `get_concept`
Get detailed information about a specific UMLS concept using its CUI (Concept Unique Identifier).

**Parameters:**
- `cui` (string, required): Concept Unique Identifier (e.g., "C0009044")

**Example:**
```
Get details for concept C0009044 (Closed Fracture)
```

#### 3. `get_definitions`
Get all definitions for a concept from various medical vocabularies.

**Parameters:**
- `cui` (string, required): Concept Unique Identifier

**Example:**
```
Get definitions for diabetes mellitus concept
```

#### 4. `get_concept_relations`
Get relationships between concepts (parent concepts, child concepts, related terms).

**Parameters:**
- `cui` (string, required): Concept Unique Identifier
- `page_size` (integer, optional): Number of results (1-25, default: 10)

**Example:**
```
Get parent and child concepts for diabetes mellitus
```

#### 5. `crosswalk_codes`
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

#### 6. `get_source_concept`
Get information about a specific code from a particular medical vocabulary.

**Parameters:**
- `source` (string, required): Source vocabulary abbreviation
- `code` (string, required): The code in that vocabulary

**Example:**
```
Get information about ICD-10 code E11.9
```

### VSAC Tools

#### 7. `search_value_sets`
Search the VSAC for curated value sets by title, keyword, publisher, or contained code.

**Parameters:**
- `title` (string, optional): Search by title (e.g., "Diabetes", "Hypertension")
- `keyword` (string, optional): Search by keyword/tag
- `publisher` (string, optional): Filter by publishing organization (e.g., "Mathematica", "NCQA")
- `code` (string, optional): Find value sets containing a specific code
- `count` (integer, optional): Number of results (default: 10)

**Example:**
```
Search for value sets related to "Diabetes" to find eCQM-relevant code groupings
```

#### 8. `get_value_set`
Get a value set definition by its OID (Object Identifier).

**Parameters:**
- `oid` (string, required): The value set OID (e.g., "2.16.840.1.113883.3.464.1003.103.12.1001")

**Example:**
```
Get the definition of the Diabetes value set used in CMS quality measures
```

#### 9. `expand_value_set`
Expand a value set to get all its member codes. Returns every code with its code system, value, and display name.

**Parameters:**
- `oid` (string, required): The value set OID
- `filter` (string, optional): Text to filter codes within the expansion
- `count` (integer, optional): Number of codes to return (default: 100)
- `offset` (integer, optional): Starting offset for pagination (default: 0)

**Example:**
```
Expand the Diabetes value set to get all ICD-10 and SNOMED codes it contains
```

#### 10. `validate_code_in_value_set`
Check if a specific code is a member of a value set.

**Parameters:**
- `oid` (string, required): The value set OID to check against
- `code` (string, required): The code to validate
- `system` (string, optional): Code system URI (required if the value set spans multiple code systems)

**Common code system URIs:**
- `http://snomed.info/sct` - SNOMED CT
- `http://hl7.org/fhir/sid/icd-10-cm` - ICD-10-CM
- `http://loinc.org` - LOINC
- `http://www.nlm.nih.gov/research/umls/rxnorm` - RxNorm
- `http://www.ama-assn.org/go/cpt` - CPT

**Example:**
```
Check if ICD-10 code E11.9 is in the Diabetes value set for eCQM reporting
```

#### 11. `lookup_code`
Look up details about a specific code in a code system via VSAC.

**Parameters:**
- `system` (string, required): Code system URI (see common URIs above)
- `code` (string, required): The code to look up
- `version` (string, optional): Code system version

**Example:**
```
Look up SNOMED CT code 44054006 to get its display name and properties
```

#### 12. `check_code_subsumption`
Test whether one code subsumes (is an ancestor of) another in a hierarchical code system.

**Parameters:**
- `system` (string, required): Code system URI (e.g., "http://snomed.info/sct")
- `code_a` (string, required): The potential ancestor/broader code
- `code_b` (string, required): The potential descendant/narrower code

**Returns:** "subsumes", "subsumed-by", "equivalent", or "not-subsumed"

**Example:**
```
Check if SNOMED "Diabetes mellitus" subsumes "Type 2 diabetes mellitus"
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

### Example 4: Finding Value Set Codes for Quality Measures
```
User: "What codes count as Diabetes for eCQM reporting?"

AI uses search_value_sets with title "Diabetes" to find relevant value sets,
then uses expand_value_set to get all member codes (ICD-10, SNOMED CT, etc.)
from the appropriate value set.
```

### Example 5: Validating a Code Against a Value Set
```
User: "Does ICD-10 code E11.9 qualify for the Diabetes quality measure?"

AI uses validate_code_in_value_set:
- oid: "2.16.840.1.113883.3.464.1003.103.12.1001"
- code: "E11.9"
- system: "http://hl7.org/fhir/sid/icd-10-cm"

Returns true/false indicating membership.
```

### Example 6: Checking Code Hierarchy
```
User: "Is Type 2 diabetes a subtype of diabetes mellitus in SNOMED?"

AI uses check_code_subsumption:
- system: "http://snomed.info/sct"
- code_a: "73211009" (Diabetes mellitus)
- code_b: "44054006" (Type 2 diabetes)

Returns "subsumes" confirming the hierarchical relationship.
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
│       ├── umls_client.py     # UMLS REST API client
│       └── vsac_client.py     # VSAC FHIR API client
├── examples/
│   ├── test_server.py         # Tool registration verification
│   └── client_example.py      # Live API usage example
├── pyproject.toml
└── README.md
```

## API Rate Limits

Both the UMLS and VSAC APIs share the same rate limit:
- Maximum 20 requests per second per IP address
- The server doesn't currently implement client-side rate limiting, so be mindful of usage patterns

## Troubleshooting

### "UMLS_API_KEY environment variable is required"
- Ensure you've set the `UMLS_API_KEY` environment variable
- Check that the key is valid by testing it at https://documentation.uts.nlm.nih.gov/umls-api-interactive.html

### HTTP 401 Unauthorized
- Your API key may be invalid or expired
- Regenerate your API key from your UTS profile

### HTTP 404 Not Found
- The CUI, code, or value set OID you're looking up doesn't exist
- Check the spelling and format of identifiers

## Resources

- [UMLS REST API Documentation](https://documentation.uts.nlm.nih.gov/rest/home.html)
- [UMLS Metathesaurus Browser](https://uts.nlm.nih.gov/uts/umls/home)
- [VSAC FHIR API Documentation](https://www.nlm.nih.gov/vsac/support/usingvsac/vsacfhirapi.html)
- [VSAC Home](https://vsac.nlm.nih.gov/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [UMLS License Information](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html)

## Disclaimer

This is an independent, community-built project and is not an official product of the National Institutes of Health (NIH) or the National Library of Medicine (NLM). It simply provides a convenient interface to their publicly available APIs.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
