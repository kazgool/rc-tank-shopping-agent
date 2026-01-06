"""
Shopping Platforms Package

This package contains platform-specific implementations for:
- Amazon
- eMAG
- Temu
"""

from typing import Protocol, Dict, Any, Optional


class ShoppingPlatform(Protocol):
    """
    Protocol defining the interface that all platform implementations must follow.
    
    Each platform must implement:
    - name: Platform name
    - search_and_analyze: Main method to search and analyze products
    """
    
    name: str
    
    async def search_and_analyze(self, query: str, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Search for a product and analyze the results.
        
        Args:
            query: Search query string
            part: Part dictionary with specifications
            
        Returns:
            Analysis result dictionary or None
        """
        ...
