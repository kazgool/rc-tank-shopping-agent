"""
Browser Management Module

This module handles all Playwright browser automation including:
- Browser initialization with anti-detection features
- Context and session management
- Screenshot capture
- Human-like delays and interactions
"""

import asyncio
import random
from pathlib import Path
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger

from config import Config, SCREENSHOTS_DIR


class BrowserManager:
    """
    Manages Playwright browser instances with human-like behavior and anti-detection.
    
    This class provides a high-level interface for browser automation with features like:
    - Automatic browser lifecycle management
    - Screenshot capture at each step
    - Random delays to mimic human behavior
    - Cookie and session persistence
    """
    
    def __init__(self):
        """Initialize the browser manager."""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._screenshot_counter = 0
    
    async def start(self):
        """
        Start the Playwright browser.
        
        This method initializes Playwright, launches a browser, and creates a context
        with realistic settings to avoid detection.
        """
        logger.info("Starting browser...")
        
        # Start Playwright
        self.playwright = await async_playwright().start()
        
        # Launch browser with specific options
        self.browser = await self.playwright.chromium.launch(
            headless=Config.HEADLESS_MODE,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        
        # Create browser context with realistic settings
        self.context = await self.browser.new_context(
            viewport={
                'width': Config.VIEWPORT_WIDTH,
                'height': Config.VIEWPORT_HEIGHT
            },
            user_agent=Config.USER_AGENT,
            locale='en-US',
            timezone_id='America/New_York',
            # Add extra HTTP headers to appear more human-like
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
        )
        
        # Create a new page
        self.page = await self.context.new_page()
        
        # Set default timeouts
        self.page.set_default_timeout(Config.PAGE_LOAD_TIMEOUT * 1000)
        
        logger.info(f"Browser started (headless={Config.HEADLESS_MODE})")
    
    async def stop(self):
        """
        Stop the browser and cleanup resources.
        
        This method closes all browser resources in the proper order.
        """
        logger.info("Stopping browser...")
        
        if self.page:
            await self.page.close()
        
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        logger.info("Browser stopped")
    
    async def navigate_to(self, url: str, wait_for: str = "networkidle"):
        """
        Navigate to a URL with human-like behavior.
        
        Args:
            url: The URL to navigate to
            wait_for: Wait condition ('load', 'domcontentloaded', 'networkidle')
        """
        logger.info(f"Navigating to: {url}")
        
        try:
            await self.page.goto(url, wait_until=wait_for)
            await self.random_delay()
            logger.info(f"Successfully navigated to: {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise
    
    async def take_screenshot(self, name: str = "screenshot") -> Path:
        """
        Take a screenshot of the current page.
        
        Args:
            name: Base name for the screenshot file
            
        Returns:
            Path to the saved screenshot
        """
        self._screenshot_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._screenshot_counter:03d}_{name}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        
        await self.page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        
        return filepath
    
    async def random_delay(self, min_seconds: Optional[float] = None, 
                          max_seconds: Optional[float] = None):
        """
        Wait for a random amount of time to mimic human behavior.
        
        Args:
            min_seconds: Minimum delay (uses Config.MIN_DELAY if not provided)
            max_seconds: Maximum delay (uses Config.MAX_DELAY if not provided)
        """
        min_delay = min_seconds if min_seconds is not None else Config.MIN_DELAY
        max_delay = max_seconds if max_seconds is not None else Config.MAX_DELAY
        
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Waiting for {delay:.2f} seconds...")
        await asyncio.sleep(delay)
    
    async def click_element(self, selector: str, human_like: bool = True):
        """
        Click an element with optional human-like behavior.
        
        Args:
            selector: CSS selector for the element to click
            human_like: If True, adds random delay before clicking
        """
        logger.info(f"Clicking element: {selector}")
        
        if human_like:
            await self.random_delay(0.5, 1.5)
        
        try:
            await self.page.click(selector)
            logger.info(f"Successfully clicked: {selector}")
            
            if human_like:
                await self.random_delay()
        except Exception as e:
            logger.error(f"Failed to click {selector}: {e}")
            raise
    
    async def type_text(self, selector: str, text: str, human_like: bool = True):
        """
        Type text into an input field with optional human-like behavior.
        
        Args:
            selector: CSS selector for the input field
            text: Text to type
            human_like: If True, types character by character with delays
        """
        logger.info(f"Typing into {selector}: {text}")
        
        if human_like:
            await self.random_delay(0.5, 1.5)
        
        try:
            await self.page.fill(selector, "")  # Clear field first
            
            if human_like:
                # Type character by character
                for char in text:
                    await self.page.type(selector, char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
            else:
                await self.page.fill(selector, text)
            
            logger.info(f"Successfully typed into: {selector}")
            
            if human_like:
                await self.random_delay()
        except Exception as e:
            logger.error(f"Failed to type into {selector}: {e}")
            raise
    
    async def wait_for_selector(self, selector: str, timeout: Optional[float] = None):
        """
        Wait for an element to appear on the page.
        
        Args:
            selector: CSS selector to wait for
            timeout: Maximum time to wait in seconds (uses default if not provided)
        """
        timeout_ms = (timeout * 1000) if timeout else Config.PAGE_LOAD_TIMEOUT * 1000
        
        logger.info(f"Waiting for selector: {selector}")
        try:
            await self.page.wait_for_selector(selector, timeout=timeout_ms)
            logger.info(f"Selector found: {selector}")
        except Exception as e:
            logger.error(f"Timeout waiting for {selector}: {e}")
            raise
    
    async def get_page_content(self) -> str:
        """
        Get the HTML content of the current page.
        
        Returns:
            HTML content as string
        """
        return await self.page.content()
    
    async def scroll_page(self, direction: str = "down", distance: int = 500):
        """
        Scroll the page in the specified direction.
        
        Args:
            direction: 'down' or 'up'
            distance: Pixels to scroll
        """
        logger.info(f"Scrolling {direction} by {distance}px")
        
        scroll_distance = distance if direction == "down" else -distance
        await self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await self.random_delay(0.5, 1.0)
    
    async def save_cookies(self, filepath: Path):
        """
        Save browser cookies to a file.
        
        Args:
            filepath: Path where to save cookies
        """
        import json
        
        cookies = await self.context.cookies()
        with open(filepath, 'w') as f:
            json.dump(cookies, f)
        logger.info(f"Cookies saved to: {filepath}")
    
    async def load_cookies(self, filepath: Path):
        """
        Load browser cookies from a file.
        
        Args:
            filepath: Path to cookies file
        """
        import json
        
        if not filepath.exists():
            logger.warning(f"Cookie file not found: {filepath}")
            return
        
        with open(filepath, 'r') as f:
            cookies = json.load(f)
        
        await self.context.add_cookies(cookies)
        logger.info(f"Cookies loaded from: {filepath}")
    
    def __enter__(self):
        """Context manager entry (not async - use async with instead)."""
        raise TypeError("Use 'async with' instead of 'with'")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
        return False
