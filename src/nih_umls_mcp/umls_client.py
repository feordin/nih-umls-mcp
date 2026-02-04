"""Client for interacting with the NIH UMLS REST API."""

import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode


class UMLSClient:
    """Client for the NIH UMLS REST API.
    
    The UMLS (Unified Medical Language System) integrates biomedical terminology
    from many sources and provides a mapping structure among these vocabularies.
    
    Authentication is via API key which can be obtained from:
    https://uts.nlm.nih.gov/uts/signup-login
    
    Note: This client maintains an HTTP connection. Call close() when done,
    or use the client as a context manager with the 'with' statement.
    """
    
    BASE_URL = "https://uts-ws.nlm.nih.gov/rest"
    
    def __init__(self, api_key: str, version: str = "current"):
        """Initialize the UMLS client.
        
        Args:
            api_key: Your UMLS API key
            version: UMLS version to use (default: "current")
        """
        self.api_key = api_key
        self.version = version
        self.client = httpx.Client(timeout=30.0)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures client is closed."""
        self.close()
        return False
    
    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build a complete URL with API key authentication."""
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        if params:
            url += f"?{urlencode(params)}"
        return url
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the UMLS API."""
        url = self._build_url(endpoint, params)
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    def search(
        self,
        query: str,
        input_type: str = "atom",
        search_type: str = "words",
        page_size: int = 25,
        page_number: int = 1
    ) -> Dict[str, Any]:
        """Search for UMLS concepts.
        
        Args:
            query: Search term or code
            input_type: Type of input - "atom", "code", "sourceConcept", "sourceDescriptor", "sourceUi", "tty"
            search_type: Type of search - "exact", "words", "leftTruncation", "rightTruncation", "normalizedString", "approximate"
            page_size: Number of results per page (max 25)
            page_number: Page number to retrieve
            
        Returns:
            Search results containing CUIs and concept information
        """
        params = {
            "string": query,
            "inputType": input_type,
            "searchType": search_type,
            "pageSize": min(page_size, 25),
            "pageNumber": page_number
        }
        return self._get(f"search/{self.version}", params)
    
    def get_cui(self, cui: str) -> Dict[str, Any]:
        """Get detailed information about a concept by its CUI.
        
        Args:
            cui: Concept Unique Identifier (e.g., "C0009044")
            
        Returns:
            Detailed concept information including names, semantics, and relationships
        """
        return self._get(f"content/{self.version}/CUI/{cui}")
    
    def get_definitions(self, cui: str) -> Dict[str, Any]:
        """Get definitions for a concept.
        
        Args:
            cui: Concept Unique Identifier
            
        Returns:
            Definitions from various sources
        """
        return self._get(f"content/{self.version}/CUI/{cui}/definitions")
    
    def get_atoms(self, cui: str, page_size: int = 25, page_number: int = 1) -> Dict[str, Any]:
        """Get atoms (terms) associated with a concept.
        
        Args:
            cui: Concept Unique Identifier
            page_size: Number of results per page
            page_number: Page number to retrieve
            
        Returns:
            Atoms (terms) for the concept from various vocabularies
        """
        params = {
            "pageSize": min(page_size, 25),
            "pageNumber": page_number
        }
        return self._get(f"content/{self.version}/CUI/{cui}/atoms", params)
    
    def get_relations(
        self,
        cui: str,
        page_size: int = 25,
        page_number: int = 1
    ) -> Dict[str, Any]:
        """Get relationships for a concept.
        
        Args:
            cui: Concept Unique Identifier
            page_size: Number of results per page
            page_number: Page number to retrieve
            
        Returns:
            Concept relationships (parent, child, sibling concepts, etc.)
        """
        params = {
            "pageSize": min(page_size, 25),
            "pageNumber": page_number
        }
        return self._get(f"content/{self.version}/CUI/{cui}/relations", params)
    
    def get_source_concept(self, source: str, source_id: str) -> Dict[str, Any]:
        """Get information about a source-asserted identifier.
        
        Args:
            source: Source vocabulary (e.g., "SNOMEDCT_US", "ICD10CM", "RXNORM")
            source_id: Identifier in the source vocabulary
            
        Returns:
            Information about the source concept
        """
        return self._get(f"content/{self.version}/source/{source}/{source_id}")
    
    def crosswalk(
        self,
        source: str,
        source_id: str,
        target_source: Optional[str] = None,
        page_size: int = 25,
        page_number: int = 1
    ) -> Dict[str, Any]:
        """Map a code from one vocabulary to codes in other vocabularies.
        
        This is useful for converting between different medical coding systems
        (e.g., ICD-10 to SNOMED CT).
        
        Args:
            source: Source vocabulary abbreviation
            source_id: Identifier in the source vocabulary
            target_source: Optional target vocabulary to filter results
            page_size: Number of results per page
            page_number: Page number to retrieve
            
        Returns:
            Equivalent codes in other vocabularies that share the same CUI
        """
        params = {
            "pageSize": min(page_size, 25),
            "pageNumber": page_number
        }
        if target_source:
            params["targetSource"] = target_source
            
        return self._get(f"crosswalk/{self.version}/source/{source}/{source_id}", params)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
