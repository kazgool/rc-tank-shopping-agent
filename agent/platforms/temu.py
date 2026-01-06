"""
Temu Platform Integration

This module handles Temu-specific shopping automation including:
- Search functionality
- Product page analysis
- Add to cart/wishlist
- Login handling

Temu is a global e-commerce platform with competitive pricing.
"""

from typing import Dict, Any, Optional
from loguru import logger

from config import Config


class TemuPlatform:
    """
    Temu platform handler for automated shopping.
    
    This class implements Temu-specific:
    - Search URL formatting
    - Page element selectors
    - Product extraction logic
    - Cart/wishlist operations
    """
    
    def __init__(self, browser_manager, gpt_agent):
        """
        Initialize Temu platform handler.
        
        Args:
            browser_manager: BrowserManager instance
            gpt_agent: GPTVisionAgent instance
        """
        self.name = "Temu"
        self.browser = browser_manager
        self.gpt = gpt_agent
        self.config = Config.get_platform_config("temu")
        logger.info(f"Initialized {self.name} platform handler")
    
    async def search_and_analyze(self, query: str, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Search for a product on Temu and analyze the first result.
        
        Args:
            query: Search query string
            part: Part dictionary with name and specs
            
        Returns:
            Analysis result dictionary or None if search failed
        """
        logger.info(f"[{self.name}] Searching for: {query}")
        
        try:
            # Navigate to Temu search
            search_url = self.config["search_url"].format(query=query.replace(" ", "+"))
            await self.browser.navigate_to(search_url)
            
            # Take screenshot of search results
            await self.browser.take_screenshot(f"{self.name}_search_{query[:30]}")
            
            # Wait for search results to load (Temu might take longer to load)
            await self.browser.random_delay(3, 5)
            
            # Temu-specific selectors for product listings
            product_selectors = [
                '[class*="product-item"]',
                '[class*="goods-item"]',
                '[data-testid="product-card"]',
                '.product-card'
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
                '[class*="product-item"] a',
                '[class*="goods-item"] a',
                '[data-testid="product-card"] a',
                '.product-card a'
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
            
            # Wait for product page to load (Temu pages can take longer)
            await self.browser.random_delay(3, 5)
            
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
        Add the current product to Temu cart.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"[{self.name}] Attempting to add product to cart")
        
        try:
            # Common Temu "Add to Cart" button selectors
            add_to_cart_selectors = [
                '[class*="add-to-cart"]',
                'button[class*="AddToCart"]',
                '[data-testid="add-to-cart-button"]',
                '.cart-button'
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
        Add the current product to Temu wishlist.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"[{self.name}] Attempting to add product to wishlist")
        
        try:
            # Common Temu wishlist button selectors
            wishlist_selectors = [
                '[class*="wishlist"]',
                '[data-testid="wishlist-button"]',
                'button[class*="Favorite"]',
                '.favorite-button'
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
        Login to Temu account.
        
        Returns:
            True if login successful, False otherwise
        """
        if not Config.TEMU_EMAIL or not Config.TEMU_PASSWORD:
            logger.warning(f"[{self.name}] Login credentials not configured")
            return False
        
        logger.info(f"[{self.name}] Attempting to login")
        
        try:
            # Navigate to Temu home page first
            await self.browser.navigate_to("https://www.temu.com")
            await self.browser.random_delay(2, 3)
            
            # Look for login/signin button
            login_button_selectors = [
                '[class*="login"]',
                '[class*="signin"]',
                'a[href*="login"]',
                'button[class*="Login"]'
            ]
            
            # Click on login button
            for selector in login_button_selectors:
                try:
                    await self.browser.click_element(selector, human_like=True)
                    break
                except Exception:
                    continue
            
            await self.browser.random_delay(2, 3)
            
            # Enter email (selectors may vary)
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email"]'
            ]
            
            for selector in email_selectors:
                try:
                    await self.browser.type_text(selector, Config.TEMU_EMAIL, human_like=True)
                    break
                except Exception:
                    continue
            
            # Enter password
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]'
            ]
            
            for selector in password_selectors:
                try:
                    await self.browser.type_text(selector, Config.TEMU_PASSWORD, human_like=True)
                    break
                except Exception:
                    continue
            
            # Click submit button
            submit_selectors = [
                'button[type="submit"]',
                'button[class*="submit"]',
                'button[class*="Login"]'
            ]
            
            for selector in submit_selectors:
                try:
                    await self.browser.click_element(selector, human_like=True)
                    break
                except Exception:
                    continue
            
            # Wait for login to complete
            await self.browser.random_delay(3, 5)
            
            # Check if login was successful (simple check)
            current_url = self.browser.page.url
            if 'login' not in current_url.lower():
                logger.info(f"[{self.name}] Login successful")
                return True
            else:
                logger.warning(f"[{self.name}] Login may have failed")
                return False
                
        except Exception as e:
            logger.error(f"[{self.name}] Error during login: {e}")
            return False
