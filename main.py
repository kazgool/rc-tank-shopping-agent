#!/usr/bin/env python3
"""
RC Tank Shopping Agent - Main Entry Point

This is the command-line interface for the shopping agent.
Run this script to start searching for RC tank parts across multiple platforms.
"""

import sys
import asyncio
import argparse
from pathlib import Path

from loguru import logger

from config import Config, DATA_DIR
from agent.shopping_agent import ShoppingAgent


def setup_command():
    """
    Handle the setup command - guides user through initial setup.
    """
    print("\n" + "="*70)
    print("RC TANK SHOPPING AGENT - SETUP")
    print("="*70 + "\n")
    
    print("Welcome! Let's set up your shopping agent.\n")
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✓ Found .env file")
    else:
        print("✗ No .env file found")
        print("\nCreating .env file from template...")
        
        # Copy .env.example to .env
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✓ Created .env file")
        else:
            print("✗ .env.example not found. Please create it manually.")
            return
    
    print("\n" + "-"*70)
    print("NEXT STEPS:")
    print("-"*70)
    print("1. Open the .env file in your text editor")
    print("2. Add your OpenAI API key:")
    print("   OPENAI_API_KEY=your_actual_api_key_here")
    print("\n   Get your API key from: https://platform.openai.com/api-keys")
    print("\n3. (Optional) Configure platform credentials if you want to login")
    print("4. Save the .env file")
    print("5. Run: python main.py --shop")
    print("-"*70 + "\n")
    
    # Check if Playwright is installed
    print("Checking Playwright installation...")
    try:
        from playwright.sync_api import sync_playwright
        print("✓ Playwright is installed")
        
        # Check if browsers are installed
        try:
            with sync_playwright() as p:
                print("✓ Playwright browsers are installed")
        except Exception:
            print("✗ Playwright browsers not installed")
            print("\nInstalling Playwright browsers...")
            import subprocess
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
            print("✓ Browsers installed")
            
    except ImportError:
        print("✗ Playwright not installed")
        print("\nPlease run: pip install -r requirements.txt")
        return
    
    print("\n✓ Setup complete! You're ready to run the shopping agent.")
    print("  Run: python main.py --shop\n")


async def shop_command(args):
    """
    Handle the shop command - run the shopping agent.
    
    Args:
        args: Parsed command-line arguments
    """
    print("\n" + "="*70)
    print("RC TANK SHOPPING AGENT")
    print("="*70 + "\n")
    
    # Determine parts file
    if args.file:
        parts_file = Path(args.file)
    else:
        # Default to CSV in data directory
        parts_file = DATA_DIR / "parts_list.csv"
    
    if not parts_file.exists():
        logger.error(f"Parts file not found: {parts_file}")
        print(f"\n✗ Error: Parts file not found: {parts_file}")
        print("\nAvailable files in data directory:")
        for f in DATA_DIR.glob("*.csv"):
            print(f"  - {f.name}")
        for f in DATA_DIR.glob("*.json"):
            print(f"  - {f.name}")
        return
    
    logger.info(f"Using parts file: {parts_file}")
    print(f"Parts file: {parts_file}")
    print(f"Add to cart: {args.add_to_cart}")
    print()
    
    # Create and run shopping agent
    agent = ShoppingAgent()
    
    try:
        await agent.run(parts_file, add_to_cart=args.add_to_cart)
        print("\n✓ Shopping agent completed successfully!")
        print(f"  Check output/reports/ for detailed results")
        print(f"  Check output/screenshots/ for page captures")
        print(f"  Check output/logs/ for detailed logs\n")
    except Exception as e:
        logger.exception("Error running shopping agent")
        print(f"\n✗ Error: {e}")
        print("  Check output/logs/shopping_agent.log for details\n")
        sys.exit(1)


def report_command():
    """
    Handle the report command - display latest shopping report.
    """
    from config import REPORTS_DIR
    import json
    
    print("\n" + "="*70)
    print("RC TANK SHOPPING AGENT - LATEST REPORT")
    print("="*70 + "\n")
    
    # Find the latest report
    reports = sorted(REPORTS_DIR.glob("shopping_report_*.txt"))
    
    if not reports:
        print("No reports found. Run the shopping agent first with: python main.py --shop\n")
        return
    
    latest_report = reports[-1]
    print(f"Report: {latest_report.name}\n")
    
    # Display the text report
    with open(latest_report, 'r') as f:
        print(f.read())


def main():
    """
    Main entry point for the RC Tank Shopping Agent CLI.
    """
    parser = argparse.ArgumentParser(
        description="AI-Powered Shopping Agent for RC Tank Parts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time setup
  python main.py --setup
  
  # Run shopping agent with default parts list
  python main.py --shop
  
  # Run with custom parts file
  python main.py --shop --file my_parts.csv
  
  # Run and automatically add items to cart (use with caution!)
  python main.py --shop --add-to-cart
  
  # View latest report
  python main.py --report
        """
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run initial setup wizard"
    )
    
    parser.add_argument(
        "--shop",
        action="store_true",
        help="Run the shopping agent"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Display the latest shopping report"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Path to parts list file (CSV or JSON). Default: data/parts_list.csv"
    )
    
    parser.add_argument(
        "--add-to-cart",
        action="store_true",
        help="Automatically add matched items to cart (default: False)"
    )
    
    args = parser.parse_args()
    
    # If no command specified, show help
    if not (args.setup or args.shop or args.report):
        parser.print_help()
        sys.exit(0)
    
    # Execute the requested command
    if args.setup:
        setup_command()
    
    if args.shop:
        asyncio.run(shop_command(args))
    
    if args.report:
        report_command()


if __name__ == "__main__":
    main()
