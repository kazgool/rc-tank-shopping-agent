"""
Main Shopping Agent Module

This is the core orchestration module that coordinates:
- Loading part lists
- Browser automation
- GPT-4 Vision analysis
- Platform-specific shopping logic
- Report generation
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
from loguru import logger
from tqdm import tqdm

from config import Config, DATA_DIR, REPORTS_DIR
from agent.browser import BrowserManager
from agent.gpt_vision import GPTVisionAgent
from agent.platforms.amazon import AmazonPlatform
from agent.platforms.emag import EmagPlatform
from agent.platforms.temu import TemuPlatform


class ShoppingAgent:
    """
    Main shopping agent that orchestrates the entire shopping automation process.
    
    This agent:
    1. Loads part lists from CSV/JSON
    2. For each part, searches across all enabled platforms
    3. Uses GPT-4 Vision to analyze and select products
    4. Adds selected products to cart/wishlist
    5. Generates comprehensive shopping reports
    """
    
    def __init__(self):
        """Initialize the shopping agent."""
        self.browser_manager = BrowserManager()
        self.gpt_agent = GPTVisionAgent()
        self.platforms = []
        self.results = []
        logger.info("Shopping agent initialized")
    
    def _initialize_platforms(self):
        """Initialize all enabled platform handlers."""
        self.platforms = []
        
        if Config.PLATFORMS["amazon"]["enabled"]:
            self.platforms.append(AmazonPlatform(self.browser_manager, self.gpt_agent))
        
        if Config.PLATFORMS["emag"]["enabled"]:
            self.platforms.append(EmagPlatform(self.browser_manager, self.gpt_agent))
        
        if Config.PLATFORMS["temu"]["enabled"]:
            self.platforms.append(TemuPlatform(self.browser_manager, self.gpt_agent))
        
        logger.info(f"Initialized {len(self.platforms)} platforms: {[p.name for p in self.platforms]}")
    
    def load_parts_from_csv(self, csv_path: Path) -> List[Dict[str, Any]]:
        """
        Load parts list from a CSV file.
        
        Expected CSV format:
        part_name,category,voltage,rpm,other_specs...
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of part dictionaries
        """
        logger.info(f"Loading parts from CSV: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            parts = []
            
            for _, row in df.iterrows():
                part = {
                    "name": row.get("part_name", row.get("name", "Unknown")),
                    "category": row.get("category", "General"),
                    "specs": {}
                }
                
                # Add all other columns as specifications
                for col in df.columns:
                    if col not in ["part_name", "name", "category"] and pd.notna(row[col]):
                        part["specs"][col] = row[col]
                
                parts.append(part)
            
            logger.info(f"Loaded {len(parts)} parts from CSV")
            return parts
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_parts_from_json(self, json_path: Path) -> List[Dict[str, Any]]:
        """
        Load parts list from a JSON file.
        
        Expected JSON format:
        [
            {
                "name": "DC Motor",
                "category": "Motors",
                "specs": {"voltage": "12V", "rpm": "300"}
            },
            ...
        ]
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            List of part dictionaries
        """
        logger.info(f"Loading parts from JSON: {json_path}")
        
        try:
            with open(json_path, 'r') as f:
                parts = json.load(f)
            
            logger.info(f"Loaded {len(parts)} parts from JSON")
            return parts
            
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            raise
    
    async def search_part_on_platform(self, platform, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Search for a specific part on a given platform.
        
        Args:
            platform: Platform handler instance
            part: Part dictionary with name and specs
            
        Returns:
            Dictionary with search results or None if search failed
        """
        logger.info(f"Searching for '{part['name']}' on {platform.name}")
        
        try:
            # Generate optimized search query using GPT-4
            search_query = self.gpt_agent.generate_search_query(
                part['name'],
                part['specs']
            )
            
            # Perform search on the platform
            result = await platform.search_and_analyze(search_query, part)
            
            if result:
                result['platform'] = platform.name
                result['search_query'] = search_query
                logger.info(f"Found match on {platform.name}: {result.get('confidence', 0):.2f} confidence")
            else:
                logger.warning(f"No suitable match found on {platform.name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching on {platform.name}: {e}")
            return None
    
    async def process_part(self, part: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single part: search across all platforms and select the best match.
        
        Args:
            part: Part dictionary
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing part: {part['name']}")
        logger.info(f"Specifications: {part['specs']}")
        logger.info(f"{'='*60}")
        
        part_result = {
            "part_name": part['name'],
            "category": part.get('category', 'General'),
            "specs": part['specs'],
            "platform_results": [],
            "best_match": None,
            "status": "pending"
        }
        
        # Search on all platforms
        for platform in self.platforms:
            try:
                result = await self.search_part_on_platform(platform, part)
                if result:
                    part_result["platform_results"].append(result)
            except Exception as e:
                logger.error(f"Error processing {part['name']} on {platform.name}: {e}")
        
        # Compare results and select best match
        if part_result["platform_results"]:
            comparison = self.gpt_agent.compare_products(
                part_result["platform_results"],
                part['name'],
                part['specs']
            )
            
            part_result["best_match"] = comparison.get("best_product")
            part_result["comparison_reasoning"] = comparison.get("reasoning", "")
            
            if part_result["best_match"]:
                part_result["status"] = "found"
                logger.info(f"✓ Best match selected from {part_result['best_match'].get('platform')}")
            else:
                part_result["status"] = "no_suitable_match"
                logger.warning("✗ No suitable match found on any platform")
        else:
            part_result["status"] = "search_failed"
            logger.error("✗ Search failed on all platforms")
        
        return part_result
    
    async def run(self, parts_file: Path, add_to_cart: bool = False):
        """
        Run the shopping agent on a list of parts.
        
        Args:
            parts_file: Path to parts list file (CSV or JSON)
            add_to_cart: If True, automatically add items to cart (default: False for safety)
        """
        logger.info(f"Starting shopping agent with file: {parts_file}")
        
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        
        # Load parts list
        if parts_file.suffix.lower() == '.csv':
            parts = self.load_parts_from_csv(parts_file)
        elif parts_file.suffix.lower() == '.json':
            parts = self.load_parts_from_json(parts_file)
        else:
            raise ValueError(f"Unsupported file format: {parts_file.suffix}. Use .csv or .json")
        
        if not parts:
            logger.error("No parts loaded. Exiting.")
            return
        
        # Start browser
        await self.browser_manager.start()
        
        try:
            # Initialize platforms
            self._initialize_platforms()
            
            # Process each part with progress bar
            logger.info(f"\nProcessing {len(parts)} parts across {len(self.platforms)} platforms...")
            
            for part in tqdm(parts, desc="Processing parts", unit="part"):
                result = await self.process_part(part)
                self.results.append(result)
                
                # Optional: Add to cart if requested and match found
                if add_to_cart and result["best_match"]:
                    logger.info(f"Add to cart functionality would be triggered here for: {part['name']}")
                    # TODO: Implement actual add to cart when ready
            
            # Generate report
            report_path = await self.generate_report()
            logger.info(f"\n{'='*60}")
            logger.info(f"Shopping agent completed!")
            logger.info(f"Report saved to: {report_path}")
            logger.info(f"{'='*60}")
            
        finally:
            # Always cleanup browser
            await self.browser_manager.stop()
    
    async def generate_report(self) -> Path:
        """
        Generate a comprehensive shopping report.
        
        Returns:
            Path to the generated report file
        """
        logger.info("Generating shopping report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPORTS_DIR / f"shopping_report_{timestamp}.json"
        
        # Prepare report data
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_parts": len(self.results),
            "found": sum(1 for r in self.results if r["status"] == "found"),
            "not_found": sum(1 for r in self.results if r["status"] != "found"),
            "platforms_checked": [p.name for p in self.platforms],
            "results": self.results
        }
        
        # Save JSON report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also create a human-readable text report
        text_report_path = REPORTS_DIR / f"shopping_report_{timestamp}.txt"
        await self._generate_text_report(text_report_path, report)
        
        logger.info(f"Reports generated: {report_path} and {text_report_path}")
        return report_path
    
    async def _generate_text_report(self, path: Path, report: Dict):
        """Generate a human-readable text report."""
        with open(path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("RC TANK SHOPPING AGENT - REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Generated: {report['timestamp']}\n")
            f.write(f"Total Parts: {report['total_parts']}\n")
            f.write(f"Found: {report['found']}\n")
            f.write(f"Not Found: {report['not_found']}\n")
            f.write(f"Platforms: {', '.join(report['platforms_checked'])}\n\n")
            
            f.write("="*70 + "\n")
            f.write("DETAILED RESULTS\n")
            f.write("="*70 + "\n\n")
            
            for i, result in enumerate(report['results'], 1):
                f.write(f"\n{i}. {result['part_name']} ({result['category']})\n")
                f.write(f"   Status: {result['status']}\n")
                f.write(f"   Specifications: {result['specs']}\n\n")
                
                if result['platform_results']:
                    f.write(f"   Found on {len(result['platform_results'])} platform(s):\n")
                    for pr in result['platform_results']:
                        f.write(f"   - {pr.get('platform', 'Unknown')}: ")
                        f.write(f"Confidence {pr.get('confidence', 0):.2f}, ")
                        f.write(f"Price: {pr.get('price', 'N/A')}\n")
                
                if result['best_match']:
                    f.write(f"\n   ★ BEST MATCH: {result['best_match'].get('platform')}\n")
                    f.write(f"     Price: {result['best_match'].get('price', 'N/A')}\n")
                    f.write(f"     Confidence: {result['best_match'].get('confidence', 0):.2f}\n")
                    f.write(f"     Reasoning: {result.get('comparison_reasoning', 'N/A')}\n")
                
                f.write("\n" + "-"*70 + "\n")
