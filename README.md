# NIH UMLS MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with seamless access to the NIH UMLS (Unified Medical Language System) API.

## About UMLS

The [Unified Medical Language System (UMLS)](https://www.nlm.nih.gov/research/umls/index.html) is a comprehensive system maintained by the U.S. National Library of Medicine (NLM) that integrates over 160 biomedical vocabularies, coding standards, and classification systems. These include widely used terminologies like SNOMED CT, MeSH, LOINC, and ICD-10-CM.

The UMLS API enables:
- **Interoperability** between different health and biomedical information systems
- **Search and retrieval** of medical concepts, terms, codes, and their relationships
- **Mapping and linking** between different coding systems and clinical terminologies
- **Integration** of standardized medical terminology into healthcare IT applications

## Purpose

This MCP server acts as a bridge between AI assistants (like Claude, ChatGPT, or other MCP-compatible systems) and the NIH UMLS API. It allows AI models to:

- Query medical concepts and terminology in real-time
- Access standardized biomedical vocabulary data
- Retrieve mappings between different medical coding systems
- Navigate hierarchical relationships in medical terminologies
- Provide context-aware responses using authoritative medical knowledge

By exposing UMLS capabilities through the Model Context Protocol, this server enables AI assistants to incorporate standardized medical terminology and knowledge into their responses without requiring manual API integration.

## Prerequisites

### UMLS API Key Required

**You must have your own UMLS API key to use this server.** API keys are free but require:

1. **Creating a UMLS Terminology Services (UTS) account** at [https://uts.nlm.nih.gov/](https://uts.nlm.nih.gov/)
2. **Applying for a UMLS license** (free for individuals, approval typically takes up to 5 days)
3. **Retrieving your API key** from your UTS profile after approval

To obtain your API key:
- Sign in to [UTS](https://uts.nlm.nih.gov/)
- Go to "My Profile"
- Your API key will be displayed there
- If needed, click "Edit Profile" → check "Generate new API Key" → Save

For more information, see the [official UMLS authentication documentation](https://documentation.uts.nlm.nih.gov/rest/authentication.html).

## Installation

```bash
# Installation instructions will be added as the server is developed
```

## Usage

```bash
# Usage instructions will be added as the server is developed
```

## License

See [LICENSE](LICENSE) file for details.
