"""Example usage of the UMLS client (for testing with a real API key).

This demonstrates the basic functionality of the UMLS client without MCP.
To run this, you need a valid UMLS API key set in the environment.

Usage:
    export UMLS_API_KEY="your-api-key-here"
    python examples/client_example.py
"""

import asyncio
import os
import json
from nih_umls_mcp.umls_client import UMLSClient


async def main():
    """Demonstrate UMLS client functionality."""
    api_key = os.getenv("UMLS_API_KEY")

    if not api_key:
        print("ERROR: UMLS_API_KEY environment variable not set")
        print("Get your API key from: https://uts.nlm.nih.gov/uts/signup-login")
        print("Then set it: export UMLS_API_KEY='your-key-here'")
        return

    print("Initializing UMLS client...")

    # Use async context manager to ensure proper cleanup
    async with UMLSClient(api_key) as client:
        try:
            # Example 1: Search for a medical term
            print("\n" + "=" * 60)
            print("Example 1: Searching for 'diabetes mellitus'")
            print("=" * 60)

            results = await client.search("diabetes mellitus", page_size=5)
            print(f"\nFound {results.get('result', {}).get('recCount', 0)} results")

            if 'result' in results and 'results' in results['result']:
                for i, result in enumerate(results['result']['results'][:3], 1):
                    cui = result.get('ui', 'N/A')
                    name = result.get('name', 'N/A')
                    print(f"{i}. CUI: {cui} - {name}")

            # Example 2: Get concept details
            print("\n" + "=" * 60)
            print("Example 2: Getting details for C0011849 (Diabetes Mellitus)")
            print("=" * 60)

            concept = await client.get_cui("C0011849")
            if 'result' in concept:
                result = concept['result']
                print(f"\nName: {result.get('name', 'N/A')}")
                print(f"Semantic Types: {', '.join([st.get('name', '') for st in result.get('semanticTypes', [])])}")
                print(f"Atom Count: {result.get('atomCount', 'N/A')}")

            # Example 3: Get definitions
            print("\n" + "=" * 60)
            print("Example 3: Getting definitions for C0011849")
            print("=" * 60)

            definitions = await client.get_definitions("C0011849")
            if 'result' in definitions and 'results' in definitions['result']:
                for i, defn in enumerate(definitions['result']['results'][:2], 1):
                    source = defn.get('rootSource', 'N/A')
                    value = defn.get('value', 'N/A')
                    print(f"\n{i}. From {source}:")
                    print(f"   {value[:200]}...")

            # Example 4: Crosswalk (code mapping)
            print("\n" + "=" * 60)
            print("Example 4: Mapping ICD-10 code E11.9 to other systems")
            print("=" * 60)

            crosswalk = await client.crosswalk("ICD10CM", "E11.9", page_size=5)
            if 'result' in crosswalk and 'results' in crosswalk['result']:
                print(f"\nFound {len(crosswalk['result']['results'])} equivalent codes:")
                for result in crosswalk['result']['results'][:5]:
                    source = result.get('rootSource', 'N/A')
                    code = result.get('ui', 'N/A')
                    name = result.get('name', 'N/A')
                    print(f"  - {source}: {code} - {name}")

            print("\n" + "=" * 60)
            print("Examples completed successfully!")
            print("=" * 60)

        except Exception as e:
            print(f"\nError: {e}")
            print("\nMake sure your API key is valid and you have internet access.")


if __name__ == "__main__":
    asyncio.run(main())
