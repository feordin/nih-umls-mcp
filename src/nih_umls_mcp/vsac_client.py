"""Client for interacting with the NIH VSAC (Value Set Authority Center) FHIR API."""

import base64
import httpx
from typing import Optional, Dict, Any


class VSACClient:
    """Async client for the NIH VSAC FHIR Terminology Service API.

    The VSAC (Value Set Authority Center) provides access to curated value sets
    used in electronic Clinical Quality Measures (eCQMs), C-CDA documents, and
    other health IT standards. Value sets are collections of medical codes from
    standard code systems (SNOMED CT, ICD-10, LOINC, CPT, RxNorm, etc.).

    Authentication uses the same UMLS API key via HTTP Basic Auth.

    API documentation: https://www.nlm.nih.gov/vsac/support/usingvsac/vsacfhirapi.html
    """

    BASE_URL = "https://cts.nlm.nih.gov/fhir"

    def __init__(self, api_key: str):
        """Initialize the VSAC client.

        Args:
            api_key: Your UMLS API key (same key used for UMLS REST API)
        """
        self.api_key = api_key
        credentials = base64.b64encode(f"apikey:{api_key}".encode()).decode()
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Basic {credentials}",
                "Accept": "application/fhir+json",
            },
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures client is closed."""
        await self.close()
        return False

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the VSAC FHIR API."""
        url = f"{self.BASE_URL}/{path}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def search_value_sets(
        self,
        title: Optional[str] = None,
        keyword: Optional[str] = None,
        publisher: Optional[str] = None,
        code: Optional[str] = None,
        count: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search for value sets by title, keyword, publisher, or contained code.

        Args:
            title: Search value sets by title (partial match)
            keyword: Search by keyword/tag
            publisher: Filter by publishing organization
            code: Find value sets containing a specific code
            count: Number of results to return (default 10)
            offset: Starting offset for pagination

        Returns:
            FHIR Bundle of matching ValueSet resources
        """
        params: Dict[str, Any] = {"_count": count, "_offset": offset}
        if title:
            params["title:contains"] = title
        if keyword:
            params["keyword"] = keyword
        if publisher:
            params["publisher"] = publisher
        if code:
            params["code"] = code
        return await self._get("ValueSet", params)

    async def get_value_set(self, oid: str) -> Dict[str, Any]:
        """Get a value set definition by its OID.

        Args:
            oid: The value set OID (e.g., "2.16.840.1.113883.3.464.1003.103.12.1001")

        Returns:
            FHIR ValueSet resource with compose definition
        """
        return await self._get(f"ValueSet/{oid}")

    async def expand_value_set(
        self,
        oid: str,
        filter_text: Optional[str] = None,
        count: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Expand a value set to get all member codes.

        Args:
            oid: The value set OID
            filter_text: Optional text to filter codes within the expansion
            count: Number of codes to return (default 100)
            offset: Starting offset for pagination

        Returns:
            FHIR ValueSet resource with expansion containing all codes
        """
        params: Dict[str, Any] = {"count": count, "offset": offset}
        if filter_text:
            params["filter"] = filter_text
        return await self._get(f"ValueSet/{oid}/$expand", params)

    async def validate_code(
        self,
        oid: str,
        code: str,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Check if a code is a member of a value set.

        Args:
            oid: The value set OID
            code: The code to validate
            system: The code system URI (e.g., "http://snomed.info/sct").
                    Required if the value set spans multiple code systems.

        Returns:
            FHIR Parameters resource with result (true/false) and display name
        """
        params: Dict[str, Any] = {"code": code}
        if system:
            params["system"] = system
        return await self._get(f"ValueSet/{oid}/$validate-code", params)

    async def lookup_code(
        self,
        system: str,
        code: str,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Look up details about a code in a code system.

        Args:
            system: Code system URI (e.g., "http://snomed.info/sct",
                    "http://hl7.org/fhir/sid/icd-10-cm", "http://loinc.org")
            code: The code to look up
            version: Optional code system version

        Returns:
            FHIR Parameters resource with code details, display name, and properties
        """
        params: Dict[str, Any] = {"system": system, "code": code}
        if version:
            params["version"] = version
        return await self._get("CodeSystem/$lookup", params)

    async def subsumes(
        self,
        system: str,
        code_a: str,
        code_b: str,
    ) -> Dict[str, Any]:
        """Test whether code_a subsumes (is an ancestor of) code_b.

        Useful for determining hierarchical relationships between codes
        in terminologies like SNOMED CT.

        Args:
            system: Code system URI (e.g., "http://snomed.info/sct")
            code_a: The potential ancestor code
            code_b: The potential descendant code

        Returns:
            FHIR Parameters resource with outcome:
            "subsumes", "subsumed-by", "equivalent", or "not-subsumed"
        """
        params: Dict[str, Any] = {
            "system": system,
            "codeA": code_a,
            "codeB": code_b,
        }
        return await self._get("CodeSystem/$subsumes", params)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
