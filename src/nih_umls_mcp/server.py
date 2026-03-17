"""MCP Server for NIH UMLS API."""

import os
import re
import sys
import json
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .umls_client import UMLSClient
from .vsac_client import VSACClient


# Initialize the MCP server
app = Server("nih-umls-mcp")

# Global clients (will be initialized with API key from environment)
umls_client: Optional[UMLSClient] = None
vsac_client: Optional[VSACClient] = None


def _get_api_key() -> str:
    """Get the UMLS API key from environment."""
    api_key = os.getenv("UMLS_API_KEY")
    if not api_key:
        raise ValueError(
            "UMLS_API_KEY environment variable is required. "
            "Get your API key from https://uts.nlm.nih.gov/uts/signup-login"
        )
    return api_key


def get_client() -> UMLSClient:
    """Get or initialize the UMLS client."""
    global umls_client
    if umls_client is None:
        umls_client = UMLSClient(_get_api_key())
    return umls_client


def get_vsac_client() -> VSACClient:
    """Get or initialize the VSAC client."""
    global vsac_client
    if vsac_client is None:
        vsac_client = VSACClient(_get_api_key())
    return vsac_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available UMLS tools."""
    return [
        Tool(
            name="search_umls",
            description=(
                "Search the UMLS (Unified Medical Language System) Metathesaurus for medical concepts, "
                "terms, or codes. Returns CUIs (Concept Unique Identifiers, e.g. C0011849) and basic "
                "information about matching concepts. Use this tool when you have a medical term or "
                "description and need to find its UMLS CUI identifier. For looking up codes from "
                "specific terminologies (SNOMED CT, ICD-10, LOINC, RxNorm, CPT), use "
                "get_source_concept (UMLS) or lookup_code (VSAC) instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term, medical concept, or code to find"
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["exact", "words", "leftTruncation", "rightTruncation", "normalizedString", "approximate"],
                        "description": "Type of search to perform (default: words)",
                        "default": "words"
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of results to return (max 25, default 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 25
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_concept",
            description=(
                "Get detailed information about a specific UMLS concept using its CUI "
                "(Concept Unique Identifier, format: 'C' followed by 7 digits, e.g. C0011849). "
                "Returns comprehensive information including names, semantic types, and basic "
                "relationships. Use this when you already have a UMLS CUI. To look up a code "
                "from a specific terminology (SNOMED CT, ICD-10, etc.), use get_source_concept "
                "or lookup_code instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cui": {
                        "type": "string",
                        "description": "Concept Unique Identifier (e.g., C0009044)"
                    }
                },
                "required": ["cui"]
            }
        ),
        Tool(
            name="get_definitions",
            description=(
                "Get all definitions for a UMLS concept from various medical vocabularies "
                "and sources. Provides detailed explanations of what the concept means."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cui": {
                        "type": "string",
                        "description": "Concept Unique Identifier"
                    }
                },
                "required": ["cui"]
            }
        ),
        Tool(
            name="get_concept_relations",
            description=(
                "Get relationships between concepts, including parent concepts (broader terms), "
                "child concepts (narrower terms), and other related concepts. Useful for "
                "understanding the hierarchy and connections in medical terminology."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cui": {
                        "type": "string",
                        "description": "Concept Unique Identifier"
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of results to return (max 25, default 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 25
                    }
                },
                "required": ["cui"]
            }
        ),
        Tool(
            name="crosswalk_codes",
            description=(
                "Map a medical code from one coding system to equivalent codes in other systems. "
                "This is extremely useful for translating between different medical terminologies "
                "(e.g., ICD-10 to SNOMED CT, LOINC to RxNorm). All codes that share the same "
                "underlying UMLS concept will be returned."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": (
                            "Source vocabulary abbreviation (e.g., ICD10CM, SNOMEDCT_US, RXNORM, "
                            "LOINC, CPT, HCPCS, ICD9CM, ICD10PCS, NDC)"
                        )
                    },
                    "code": {
                        "type": "string",
                        "description": "The code in the source vocabulary to map from"
                    },
                    "target_source": {
                        "type": "string",
                        "description": "Optional: Specific target vocabulary to filter results"
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of results to return (max 25, default 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 25
                    }
                },
                "required": ["source", "code"]
            }
        ),
        Tool(
            name="get_source_concept",
            description=(
                "Look up a specific code from a source vocabulary (e.g., ICD-10, SNOMED CT, "
                "RxNorm, LOINC, CPT) via the UMLS Metathesaurus. Returns the code's meaning, "
                "associated UMLS CUI, and source-specific attributes. Use this when you have a "
                "code and its source vocabulary abbreviation (e.g., source='ICD10CM', code='E11.9'). "
                "For FHIR-based code lookup with code system URIs, use lookup_code instead. "
                "Do NOT pass UMLS CUIs here — use get_concept for CUI lookups."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source vocabulary abbreviation (e.g., ICD10CM, SNOMEDCT_US, RXNORM)"
                    },
                    "code": {
                        "type": "string",
                        "description": "The code in the source vocabulary"
                    }
                },
                "required": ["source", "code"]
            }
        ),
        # VSAC tools
        Tool(
            name="search_value_sets",
            description=(
                "Search the VSAC (Value Set Authority Center) for curated value sets used in "
                "clinical quality measures (eCQMs), C-CDA documents, and health IT standards. "
                "Value sets are groupings of terminology codes (SNOMED CT, ICD-10, LOINC, CPT, "
                "RxNorm) — NOT UMLS CUIs. Search by title, keyword, publisher, or find value sets "
                "containing a specific terminology code. If you need to search for a medical "
                "concept by name and get its UMLS CUI, use search_umls instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Search value sets by title (e.g., 'Diabetes', 'Hypertension')"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Search by keyword/tag"
                    },
                    "publisher": {
                        "type": "string",
                        "description": "Filter by publishing organization (e.g., 'Mathematica', 'NCQA')"
                    },
                    "code": {
                        "type": "string",
                        "description": "Find value sets containing this specific code"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to return (default 10)",
                        "default": 10,
                        "minimum": 1
                    }
                }
            }
        ),
        Tool(
            name="get_value_set",
            description=(
                "Get a value set definition by its OID (Object Identifier). "
                "Returns the value set metadata and compose definition showing "
                "which code systems and filters define its membership."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {
                        "type": "string",
                        "description": "The value set OID (e.g., '2.16.840.1.113883.3.464.1003.103.12.1001')"
                    }
                },
                "required": ["oid"]
            }
        ),
        Tool(
            name="expand_value_set",
            description=(
                "Expand a value set to get all its member codes. Returns every code "
                "(with code system, code value, and display name) that belongs to the "
                "value set. Optionally filter codes by text. Use this to answer questions "
                "like 'what ICD-10 codes define diabetes for quality reporting?'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {
                        "type": "string",
                        "description": "The value set OID"
                    },
                    "filter": {
                        "type": "string",
                        "description": "Optional text to filter codes within the expansion"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of codes to return (default 100)",
                        "default": 100,
                        "minimum": 1
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Starting offset for pagination (default 0)",
                        "default": 0,
                        "minimum": 0
                    }
                },
                "required": ["oid"]
            }
        ),
        Tool(
            name="validate_code_in_value_set",
            description=(
                "Check if a specific code is a member of a value set. Useful for "
                "clinical decision support and verifying that a code qualifies for "
                "a particular quality measure or reporting requirement."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "oid": {
                        "type": "string",
                        "description": "The value set OID to check against"
                    },
                    "code": {
                        "type": "string",
                        "description": "The code to validate"
                    },
                    "system": {
                        "type": "string",
                        "description": (
                            "Code system URI (e.g., 'http://snomed.info/sct', "
                            "'http://hl7.org/fhir/sid/icd-10-cm', 'http://loinc.org'). "
                            "Required if the value set spans multiple code systems."
                        )
                    }
                },
                "required": ["oid", "code"]
            }
        ),
        Tool(
            name="lookup_code",
            description=(
                "Look up details about a specific code in a standard terminology code system "
                "via the VSAC FHIR API. Requires a FHIR code system URI (e.g., "
                "'http://snomed.info/sct', 'http://hl7.org/fhir/sid/icd-10-cm', "
                "'http://loinc.org', 'http://www.nlm.nih.gov/research/umls/rxnorm'). "
                "Returns the code's display name, properties, and designations. "
                "This tool is for terminology codes (SNOMED, ICD-10, LOINC, RxNorm, CPT), "
                "NOT for UMLS CUIs — if you have a CUI (format: C followed by 7 digits, "
                "e.g. C0011849), use get_concept instead. For vocabulary-abbreviation-based "
                "lookup (e.g., source='SNOMEDCT_US'), use get_source_concept instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "system": {
                        "type": "string",
                        "description": (
                            "Code system URI. Common values: "
                            "'http://snomed.info/sct' (SNOMED CT), "
                            "'http://hl7.org/fhir/sid/icd-10-cm' (ICD-10-CM), "
                            "'http://loinc.org' (LOINC), "
                            "'http://www.nlm.nih.gov/research/umls/rxnorm' (RxNorm), "
                            "'http://www.ama-assn.org/go/cpt' (CPT)"
                        )
                    },
                    "code": {
                        "type": "string",
                        "description": "The code to look up"
                    },
                    "version": {
                        "type": "string",
                        "description": "Optional code system version"
                    }
                },
                "required": ["system", "code"]
            }
        ),
        Tool(
            name="check_code_subsumption",
            description=(
                "Test whether one code subsumes (is an ancestor of) another code "
                "in a hierarchical code system like SNOMED CT. Returns 'subsumes', "
                "'subsumed-by', 'equivalent', or 'not-subsumed'. Useful for clinical "
                "reasoning about hierarchical relationships between medical concepts."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "system": {
                        "type": "string",
                        "description": "Code system URI (e.g., 'http://snomed.info/sct')"
                    },
                    "code_a": {
                        "type": "string",
                        "description": "The potential ancestor/broader code"
                    },
                    "code_b": {
                        "type": "string",
                        "description": "The potential descendant/narrower code"
                    }
                },
                "required": ["system", "code_a", "code_b"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        client = get_client()
        
        if name == "search_umls":
            query = arguments["query"]
            search_type = arguments.get("search_type", "words")
            page_size = arguments.get("page_size", 10)
            
            result = await client.search(
                query=query,
                search_type=search_type,
                page_size=page_size
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_concept":
            cui = arguments["cui"]
            result = await client.get_cui(cui)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_definitions":
            cui = arguments["cui"]
            result = await client.get_definitions(cui)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_concept_relations":
            cui = arguments["cui"]
            page_size = arguments.get("page_size", 10)
            
            result = await client.get_relations(cui, page_size=page_size)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "crosswalk_codes":
            source = arguments["source"]
            code = arguments["code"]
            target_source = arguments.get("target_source")
            page_size = arguments.get("page_size", 10)
            
            result = await client.crosswalk(
                source=source,
                source_id=code,
                target_source=target_source,
                page_size=page_size
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_source_concept":
            source = arguments["source"]
            code = arguments["code"]

            try:
                result = await client.get_source_concept(source, code)
            except Exception as src_err:
                # If lookup failed and the code looks like a UMLS CUI, provide a helpful hint
                if re.match(r'^C\d{7}$', code):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": str(src_err),
                            "hint": (
                                f"The code '{code}' was not found in source vocabulary '{source}'. "
                                "This code matches the format of a UMLS CUI (Concept Unique "
                                "Identifier: 'C' followed by 7 digits). If you are looking up "
                                "a UMLS concept, use the get_concept tool instead."
                            ),
                            "suggestion": {
                                "tool": "get_concept",
                                "arguments": {"cui": code}
                            }
                        }, indent=2)
                    )]
                raise

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        # VSAC tools
        elif name == "search_value_sets":
            vsac = get_vsac_client()
            result = await vsac.search_value_sets(
                title=arguments.get("title"),
                keyword=arguments.get("keyword"),
                publisher=arguments.get("publisher"),
                code=arguments.get("code"),
                count=arguments.get("count", 10),
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_value_set":
            vsac = get_vsac_client()
            result = await vsac.get_value_set(arguments["oid"])
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "expand_value_set":
            vsac = get_vsac_client()
            result = await vsac.expand_value_set(
                oid=arguments["oid"],
                filter_text=arguments.get("filter"),
                count=arguments.get("count", 100),
                offset=arguments.get("offset", 0),
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "validate_code_in_value_set":
            vsac = get_vsac_client()
            result = await vsac.validate_code(
                oid=arguments["oid"],
                code=arguments["code"],
                system=arguments.get("system"),
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "lookup_code":
            code = arguments["code"]
            vsac = get_vsac_client()
            try:
                result = await vsac.lookup_code(
                    system=arguments["system"],
                    code=code,
                    version=arguments.get("version"),
                )
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as lookup_err:
                # If lookup failed and the code looks like a UMLS CUI, provide a helpful hint
                if re.match(r'^C\d{7}$', code):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": str(lookup_err),
                            "hint": (
                                f"The code '{code}' was not found in the specified code system. "
                                "This code matches the format of a UMLS CUI (Concept Unique "
                                "Identifier: 'C' followed by 7 digits). If you are looking up "
                                "a UMLS concept, use the get_concept tool instead."
                            ),
                            "suggestion": {
                                "tool": "get_concept",
                                "arguments": {"cui": code}
                            }
                        }, indent=2)
                    )]
                raise

        elif name == "check_code_subsumption":
            vsac = get_vsac_client()
            result = await vsac.subsumes(
                system=arguments["system"],
                code_a=arguments["code_a"],
                code_b=arguments["code_b"],
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        # Include context but avoid leaking sensitive data
        safe_args = {k: v for k, v in arguments.items() if k.lower() not in ['apikey', 'api_key', 'password', 'token']}
        return [TextContent(
            type="text",
            text=f"Error calling tool '{name}' with arguments {safe_args}: {str(e)}"
        )]


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    """Main entry point for the server."""
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
