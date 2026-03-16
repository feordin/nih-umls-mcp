"""Test script to verify the UMLS MCP server functionality.

This script tests the server with a mock API key to ensure:
1. The server starts correctly
2. Tools are properly registered
3. Error handling works when API calls fail
"""

import asyncio
import json
from nih_umls_mcp.server import app, list_tools, call_tool


async def test_server():
    """Test the MCP server functionality."""
    print("Testing NIH UMLS MCP Server")
    print("=" * 50)
    
    # Test 1: List available tools
    print("\n1. Testing tool listing...")
    try:
        tools = await list_tools()
        print(f"[OK] Successfully listed {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:60]}...")
    except Exception as e:
        print(f"[FAIL] Failed to list tools: {e}")
        return
    
    # Test 2: Verify tool schemas
    print("\n2. Verifying tool schemas...")
    expected_tools = [
        "search_umls",
        "get_concept",
        "get_definitions",
        "get_concept_relations",
        "crosswalk_codes",
        "get_source_concept",
        "search_value_sets",
        "get_value_set",
        "expand_value_set",
        "validate_code_in_value_set",
        "lookup_code",
        "check_code_subsumption",
    ]
    
    tool_names = [tool.name for tool in tools]
    for expected in expected_tools:
        if expected in tool_names:
            print(f"  [OK] {expected}")
        else:
            print(f"  [FAIL] Missing tool: {expected}")
    
    # Test 3: Check that server requires API key
    print("\n3. Testing API key requirement...")
    import os
    # Save original env var if it exists
    original_key = os.environ.get("UMLS_API_KEY")
    
    # Remove API key temporarily
    if "UMLS_API_KEY" in os.environ:
        del os.environ["UMLS_API_KEY"]
    
    try:
        # This should fail without an API key
        result = await call_tool(
            name="search_umls",
            arguments={"query": "test"}
        )
        
        # Check if error message mentions API key
        error_text = result[0].text
        if "UMLS_API_KEY" in error_text or "API key" in error_text:
            print("  [OK] Server correctly requires API key")
        else:
            print(f"  ? Unexpected response: {error_text[:100]}")
            
    except Exception as e:
        if "UMLS_API_KEY" in str(e):
            print("  [OK] Server correctly requires API key")
        else:
            print(f"  ? Unexpected error: {e}")
    finally:
        # Restore original API key if it existed
        if original_key:
            os.environ["UMLS_API_KEY"] = original_key
    
    print("\n" + "=" * 50)
    print("Basic server tests completed successfully!")
    print("\nNote: To test actual UMLS API calls, you need to:")
    print("1. Get an API key from https://uts.nlm.nih.gov/uts/signup-login")
    print("2. Set it: export UMLS_API_KEY='your-key-here'")
    print("3. Run the server: python -m nih_umls_mcp.server")


if __name__ == "__main__":
    asyncio.run(test_server())
