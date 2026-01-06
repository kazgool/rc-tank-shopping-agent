#!/usr/bin/env python3
"""
Validation script to check project setup.
Run this to verify all files are in place and properly formatted.
"""

import sys
from pathlib import Path


def check_file_exists(path, description):
    """Check if a file exists."""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} missing: {path}")
        return False


def check_directory_exists(path, description):
    """Check if a directory exists."""
    if path.is_dir():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} missing: {path}")
        return False


def main():
    """Main validation function."""
    print("\n" + "="*70)
    print("RC TANK SHOPPING AGENT - PROJECT VALIDATION")
    print("="*70 + "\n")
    
    all_good = True
    
    # Check core files
    print("Core Files:")
    all_good &= check_file_exists(Path("main.py"), "Main entry point")
    all_good &= check_file_exists(Path("config.py"), "Configuration module")
    all_good &= check_file_exists(Path("requirements.txt"), "Requirements file")
    all_good &= check_file_exists(Path(".env.example"), "Environment template")
    all_good &= check_file_exists(Path(".gitignore"), "Git ignore file")
    all_good &= check_file_exists(Path("README.md"), "Documentation")
    
    print("\nAgent Modules:")
    all_good &= check_file_exists(Path("agent/__init__.py"), "Agent package")
    all_good &= check_file_exists(Path("agent/browser.py"), "Browser manager")
    all_good &= check_file_exists(Path("agent/gpt_vision.py"), "GPT-4 Vision")
    all_good &= check_file_exists(Path("agent/shopping_agent.py"), "Shopping agent")
    
    print("\nPlatform Modules:")
    all_good &= check_file_exists(Path("agent/platforms/__init__.py"), "Platforms package")
    all_good &= check_file_exists(Path("agent/platforms/amazon.py"), "Amazon platform")
    all_good &= check_file_exists(Path("agent/platforms/emag.py"), "eMAG platform")
    all_good &= check_file_exists(Path("agent/platforms/temu.py"), "Temu platform")
    
    print("\nData Files:")
    all_good &= check_file_exists(Path("data/parts_list.csv"), "Parts list (CSV)")
    all_good &= check_file_exists(Path("data/parts_list.json"), "Parts list (JSON)")
    
    print("\nOutput Directories:")
    all_good &= check_directory_exists(Path("output/screenshots"), "Screenshots directory")
    all_good &= check_directory_exists(Path("output/reports"), "Reports directory")
    all_good &= check_directory_exists(Path("output/logs"), "Logs directory")
    
    print("\nVS Code Integration:")
    all_good &= check_file_exists(Path(".vscode/launch.json"), "Debug configurations")
    all_good &= check_file_exists(Path(".vscode/settings.json"), "Editor settings")
    all_good &= check_file_exists(Path(".vscode/extensions.json"), "Extensions")
    
    print("\n" + "="*70)
    if all_good:
        print("✓ ALL CHECKS PASSED!")
        print("\nNext steps:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run: python main.py --setup")
        print("3. Add your OpenAI API key to .env file")
        print("4. Run: python main.py --shop")
    else:
        print("✗ SOME CHECKS FAILED!")
        print("\nPlease ensure all required files are present.")
        sys.exit(1)
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
