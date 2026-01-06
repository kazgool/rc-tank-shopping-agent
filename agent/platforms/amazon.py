"""
Amazon Platform Integration

This module handles Amazon-specific shopping automation including:
- Search functionality
- Product page analysis
- Add to cart/wishlist
- Login handling
"""

from typing import Dict, Any, Optional
from loguru import logger

from config import Config


class AmazonPlatform:
    """
    Amazon platform handler for automated shopping.
    
    This class implements Amazon-specific:
    - Search URL formatting
    - Page element selectors
    - Product extraction logic
    - Cart/wishlist operations
    """
    
    def __init__(self, browser_manager, gpt_agent):
        """
        Initialize Amazon platform handler.
        
        Args:
            browser_manager: BrowserManager instance
            gpt_agent: GPTVisionAgent instance
        """
        self.name = "Amazon"
        self.browser = browser_manager
        self.gpt = gpt_agent
        self.config = Config.get_platform_config("amazon")
        logger.info(f"Initialized {self.name} platform handler")
    
    async def search_and_analyze(self, query: str, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Search for a product on Amazon and analyze the first result.
        
        Args:
            query: Search query string
            part: Part dictionary with name and specs
            
        Returns:
            Analysis result dictionary or None if search failed
        """
        logger.info(f"[{self.name}] Searching for: {query}")
        
        try:
            # Navigate to Amazon search
            search_url = self.config["search_url"].format(query=query.replace(" ", "+"))
            await self.browser.navigate_to(search_url)
            
            # Take screenshot of search results
            await self.browser.take_screenshot(f"{self.name}_search_{query[:30]}")
            
            # Wait for search results to load
            await self.browser.random_delay(2, 4)
            
            # Amazon-specific selectors (these may need adjustment based on region/changes)
            # Common selectors for product listings
            product_selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item[data-asin]',
                'div[data-cy="title-recipe"]'
            ]
            
            # Try to find products using various selectors
            product_found = False
            for selector in product_selectors:
                try:
                    await self.browser.wait_for_selector(selector, timeout=5)
                    product_found = True
                    logger.info(f"[{self.name}] Found products using selector: {selector}")
                    break
                except Exception:
                    continue
            
            if not product_found:
                logger.warning(f"[{self.name}] No products found for query: {query}")
                await self.browser.take_screenshot(f"{self.name}_no_results")
                return None
            
            # Click on the first product to view details
            # Try multiple selectors for the first product link
            first_product_selectors = [
                '[data-component-type="s-search-result"] h2 a',
                '.s-result-item h2 a',
                'h2.s-line-clamp-2 a',
                '.s-title-instructions-style a'
            ]
            
            clicked = False
            for selector in first_product_selectors:
                try:
                    await self.browser.click_element(selector, human_like=True)
                    clicked = True
                    logger.info(f"[{self.name}] Clicked product using selector: {selector}")
                    break
                except Exception:
                    continue
            
            if not clicked:
                logger.warning(f"[{self.name}] Could not click on first product")
                return None
            
            # Wait for product page to load
            await self.browser.random_delay(2, 4)
            
            # Take screenshot of product page
            screenshot_path = await self.browser.take_screenshot(
                f"{self.name}_product_{part['name'][:30]}"
            )
            
            # Use GPT-4 Vision to analyze the product page
            analysis = self.gpt.analyze_product_page(
                screenshot_path,
                part['name'],
                part['specs']
            )
            
            # Add platform-specific information
            analysis['platform'] = self.name
            analysis['product_url'] = self.browser.page.url
            
            logger.info(f"[{self.name}] Analysis complete - Match: {analysis['is_match']}, "
                       f"Confidence: {analysis['confidence']:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"[{self.name}] Error during search and analysis: {e}")
            await self.browser.take_screenshot(f"{self.name}_error")
            return None
    
    async def add_to_cart(self) -> bool:
        """
        Add the current product to Amazon cart.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"[{self.name}] Attempting to add product to cart")
        
        try:
            # Common Amazon "Add to Cart" button selectors
            add_to_cart_selectors = [
                '#add-to-cart-button',
                'input[name="submit.add-to-cart"]',
                '#add-to-cart-button-ubb',
                'button[name="submit.add-to-cart"]'
            ]
            
            for selector in add_to_cart_selectors:
                try:
                    await self.browser.click_element(selector, human_like=True)
                    logger.info(f"[{self.name}] Successfully added to cart")
                    await self.browser.take_screenshot(f"{self.name}_added_to_cart")
                    return True
                except Exception:
                    continue
            
            logger.warning(f"[{self.name}] Could not find Add to Cart button")
            return False
            
        except Exception as e:
            logger.error(f"[{self.name}] Error adding to cart: {e}")
            return False
    
    async def add_to_wishlist(self) -> bool:
        """
        Add the current product to Amazon wishlist.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"[{self.name}] Attempting to add product to wishlist")
        
        try:
            # Common Amazon wishlist button selectors
            wishlist_selectors = [
                '#add-to-wishlist-button',
                'input[name="submit.add-to-registry.wishlist"]',
                'span[id="wishListMainButton"]'
            ]
            
            for selector in wishlist_selectors:
                try:
                    await self.browser.click_element(selector, human_like=True)
                    logger.info(f"[{self.name}] Successfully added to wishlist")
                    await self.browser.take_screenshot(f"{self.name}_added_to_wishlist")
                    return True
                except Exception:
                    continue
            
            logger.warning(f"[{self.name}] Could not find Add to Wishlist button")
            return False
            
        except Exception as e:
            logger.error(f"[{self.name}] Error adding to wishlist: {e}")
            return False
    
    async def login(self) -> bool:
        """
        Login to Amazon account.
        
        Returns:
            True if login successful, False otherwise
        """
        if not Config.AMAZON_EMAIL or not Config.AMAZON_PASSWORD:
            logger.warning(f"[{self.name}] Login credentials not configured")
            return False
        
        logger.info(f"[{self.name}] Attempting to login")
        
        try:
            # Navigate to Amazon login page
            await self.browser.navigate_to("https://www.amazon.com/ap/signin")
            
            # Enter email
            await self.browser.type_text('#ap_email', Config.AMAZON_EMAIL, human_like=True)
            await self.browser.click_element('#continue', human_like=True)
            
            # Enter password
            await self.browser.type_text('#ap_password', Config.AMAZON_PASSWORD, human_like=True)
            await self.browser.click_element('#signInSubmit', human_like=True)
            
            # Wait for login to complete
            await self.browser.random_delay(3, 5)
            
            # Check if login was successful (simple check)
            current_url = self.browser.page.url
            if 'signin' not in current_url.lower():
                logger.info(f"[{self.name}] Login successful")
                return True
            else:
                logger.warning(f"[{self.name}] Login may have failed")
                return False
                
        except Exception as e:
            logger.error(f"[{self.name}] Error during login: {e}")
            return False
