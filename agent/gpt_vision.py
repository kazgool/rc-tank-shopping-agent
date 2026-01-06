"""
GPT-4 Vision Integration Module

This module provides integration with OpenAI's GPT-4 Vision API for:
- Analyzing product page screenshots
- Matching products to specifications
- Generating optimized search queries
- Product comparison across platforms
- Intelligent decision-making
"""

import base64
from pathlib import Path
from typing import Dict, List, Optional, Any

from openai import OpenAI
from loguru import logger

from config import Config


class GPTVisionAgent:
    """
    AI agent that uses GPT-4 Vision to analyze products and make shopping decisions.
    
    This class provides high-level methods for:
    - Generating search queries for parts
    - Analyzing product pages to determine if they match requirements
    - Comparing products across different platforms
    - Making purchasing decisions based on specifications
    """
    
    def __init__(self):
        """Initialize the GPT-4 Vision agent."""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please configure it in .env file.")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("GPT-4 Vision agent initialized")
    
    def _encode_image(self, image_path: Path) -> str:
        """
        Encode an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def generate_search_query(self, part_name: str, part_specs: Dict[str, Any]) -> str:
        """
        Generate an optimized search query for a specific part.
        
        This uses GPT-4 to create a search query that will work well across
        different shopping platforms.
        
        Args:
            part_name: Name of the part (e.g., "DC Motor")
            part_specs: Dictionary of specifications (e.g., {"voltage": "12V", "rpm": "300"})
            
        Returns:
            Optimized search query string
        """
        logger.info(f"Generating search query for: {part_name}")
        
        # Create a prompt for GPT-4
        specs_text = "\n".join([f"- {key}: {value}" for key, value in part_specs.items()])
        
        prompt = f"""Generate a concise and effective search query for shopping websites like Amazon, eMAG, or Temu.

Part Name: {part_name}
Specifications:
{specs_text}

Requirements:
- Keep it short (3-8 words)
- Include key specifications that help identify the exact part
- Use commonly searched terms
- Make it platform-agnostic (works on any shopping site)
- Focus on essential details that distinguish this part

Return ONLY the search query, nothing else."""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_TEXT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating effective search queries for e-commerce platforms. Generate concise, specific search terms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            query = response.choices[0].message.content.strip()
            logger.info(f"Generated search query: {query}")
            return query
            
        except Exception as e:
            logger.error(f"Error generating search query: {e}")
            # Fallback to basic query
            fallback_query = f"{part_name} {' '.join(str(v) for v in part_specs.values())}"
            logger.info(f"Using fallback query: {fallback_query}")
            return fallback_query
    
    def analyze_product_page(self, screenshot_path: Path, part_name: str, 
                           part_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a product page screenshot to determine if it matches the required part.
        
        Args:
            screenshot_path: Path to screenshot of the product page
            part_name: Name of the part we're looking for
            part_specs: Required specifications
            
        Returns:
            Dictionary with analysis results:
            {
                "is_match": bool,
                "confidence": float (0-1),
                "reasoning": str,
                "extracted_specs": dict,
                "price": str or None,
                "recommendation": str
            }
        """
        logger.info(f"Analyzing product page for: {part_name}")
        
        # Encode the screenshot
        base64_image = self._encode_image(screenshot_path)
        
        # Create detailed specifications text
        specs_text = "\n".join([f"- {key}: {value}" for key, value in part_specs.items()])
        
        prompt = f"""Analyze this product page screenshot and determine if the product matches the required specifications.

Required Part: {part_name}
Required Specifications:
{specs_text}

Please analyze:
1. Does this product match the required part type?
2. Do the visible specifications match or are compatible with requirements?
3. What is the price (if visible)?
4. What specifications can you extract from the page?
5. Would you recommend this product for the purpose?

Respond in JSON format:
{{
    "is_match": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation",
    "extracted_specs": {{"spec_name": "value"}},
    "price": "extracted price or null",
    "recommendation": "buy/skip/uncertain"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing product listings for RC tank parts. Provide accurate, detailed analysis."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            # Parse the response
            import json
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (it might be wrapped in markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            logger.info(f"Analysis complete - Match: {result.get('is_match')}, Confidence: {result.get('confidence')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing product page: {e}")
            return {
                "is_match": False,
                "confidence": 0.0,
                "reasoning": f"Error during analysis: {str(e)}",
                "extracted_specs": {},
                "price": None,
                "recommendation": "skip"
            }
    
    def compare_products(self, products: List[Dict[str, Any]], 
                        part_name: str, part_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare multiple products from different platforms and recommend the best one.
        
        Args:
            products: List of product dictionaries with analysis results
            part_name: Name of the part
            part_specs: Required specifications
            
        Returns:
            Dictionary with comparison results and recommendation
        """
        logger.info(f"Comparing {len(products)} products for: {part_name}")
        
        if not products:
            return {
                "best_product": None,
                "reasoning": "No products to compare",
                "comparison": []
            }
        
        # Create a comparison prompt
        products_text = ""
        for i, product in enumerate(products, 1):
            products_text += f"\nProduct {i} ({product.get('platform', 'Unknown')}):\n"
            products_text += f"- Price: {product.get('price', 'N/A')}\n"
            products_text += f"- Match confidence: {product.get('confidence', 0)}\n"
            products_text += f"- Specs: {product.get('extracted_specs', {})}\n"
            products_text += f"- Analysis: {product.get('reasoning', 'N/A')}\n"
        
        specs_text = "\n".join([f"- {key}: {value}" for key, value in part_specs.items()])
        
        prompt = f"""Compare these products and recommend the best one for the following requirement:

Required Part: {part_name}
Required Specifications:
{specs_text}

Available Products:
{products_text}

Consider:
1. Specification match accuracy
2. Price (best value for money)
3. Confidence in the match
4. Platform reliability

Respond in JSON format:
{{
    "best_product_index": 1-{len(products)} or null if none suitable,
    "reasoning": "detailed explanation of the choice",
    "comparison": ["brief note for product 1", "brief note for product 2", ...]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_TEXT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at comparing products and selecting the best option based on specifications and value."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse the response
            import json
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # Add the actual best product to the result
            best_index = result.get("best_product_index")
            if best_index and 1 <= best_index <= len(products):
                result["best_product"] = products[best_index - 1]
            else:
                result["best_product"] = None
            
            logger.info(f"Comparison complete - Best: Product {best_index}")
            return result
            
        except Exception as e:
            logger.error(f"Error comparing products: {e}")
            return {
                "best_product": None,
                "reasoning": f"Error during comparison: {str(e)}",
                "comparison": []
            }
    
    def optimize_part_description(self, part_name: str, part_specs: Dict[str, Any]) -> str:
        """
        Generate a detailed, optimized description for a part that can be used
        for better search and matching.
        
        Args:
            part_name: Name of the part
            part_specs: Specifications dictionary
            
        Returns:
            Optimized description string
        """
        logger.info(f"Optimizing description for: {part_name}")
        
        specs_text = "\n".join([f"- {key}: {value}" for key, value in part_specs.items()])
        
        prompt = f"""Create a detailed product description for this RC tank part that would help in accurate product matching:

Part Name: {part_name}
Specifications:
{specs_text}

Generate a concise but comprehensive description (2-3 sentences) that includes:
- The part type and its function
- Key specifications
- Common use cases or compatibility

Return only the description."""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_TEXT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in RC vehicles and components. Create accurate, detailed descriptions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            description = response.choices[0].message.content.strip()
            logger.info(f"Generated description: {description[:100]}...")
            return description
            
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return f"{part_name} with specifications: {', '.join([f'{k}={v}' for k, v in part_specs.items()])}"
