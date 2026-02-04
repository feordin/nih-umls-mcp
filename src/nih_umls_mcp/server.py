"""MCP Server for NIH UMLS API."""

import os
import sys
import json
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .umls_client import UMLSClient


# Initialize the MCP server
app = Server("nih-umls-mcp")

# Global UMLS client (will be initialized with API key from environment)
umls_client: Optional[UMLSClient] = None


def get_client() -> UMLSClient:
    """Get or initialize the UMLS client."""
    global umls_client
    
    if umls_client is None:
        api_key = os.getenv("UMLS_API_KEY")
        if not api_key:
            raise ValueError(
                "UMLS_API_KEY environment variable is required. "
                "Get your API key from https://uts.nlm.nih.gov/uts/signup-login"
            )
        umls_client = UMLSClient(api_key)
    
    return umls_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available UMLS tools."""
    return [
        Tool(
            name="search_umls",
            description=(
                "Search the UMLS (Unified Medical Language System) for medical concepts, "
                "terms, or codes. Returns CUIs (Concept Unique Identifiers) and basic "
                "information about matching concepts. Useful for finding the right concept "
                "when you have a medical term or description."
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
                "(Concept Unique Identifier). Returns comprehensive information including "
                "names, semantic types, and basic relationships. Use this after finding "
                "a CUI with search_umls."
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
                "Get information about a specific code from a particular medical vocabulary. "
                "Useful when you have a code from a specific system (like ICD-10 or SNOMED) "
                "and want to know its meaning and associated UMLS concept."
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
            
            result = client.search(
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
            result = client.get_cui(cui)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_definitions":
            cui = arguments["cui"]
            result = client.get_definitions(cui)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_concept_relations":
            cui = arguments["cui"]
            page_size = arguments.get("page_size", 10)
            
            result = client.get_relations(cui, page_size=page_size)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "crosswalk_codes":
            source = arguments["source"]
            code = arguments["code"]
            target_source = arguments.get("target_source")
            page_size = arguments.get("page_size", 10)
            
            result = client.crosswalk(
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
            
            result = client.get_source_concept(source, code)
            
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
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
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
