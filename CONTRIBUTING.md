# Contributing to RC Tank Shopping Agent

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/kazgool/rc-tank-shopping-agent/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Log files from `output/logs/`

### Suggesting Features

1. Check if the feature has been requested in [Issues](https://github.com/kazgool/rc-tank-shopping-agent/issues)
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rc-tank-shopping-agent.git
   cd rc-tank-shopping-agent
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add comments for complex logic
   - Update documentation if needed
   - Test your changes thoroughly

5. **Run validation**
   ```bash
   python validate.py
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: clear description"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe your changes clearly
   - Link any related issues

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8
- **Line Length**: 120 characters max
- **Formatter**: Black
- **Linter**: Flake8

```bash
# Format code
black .

# Check style
flake8 .
```

### Documentation

- Update README.md for major changes
- Add docstrings to all functions and classes
- Include inline comments for complex logic
- Update QUICKSTART.md if setup changes

### Testing

- Test with multiple parts lists
- Verify all three platforms work
- Check screenshots are captured
- Review log files for errors
- Test both CSV and JSON formats

### Commit Messages

Use clear, descriptive commit messages:
- ✅ "Add support for eBay platform"
- ✅ "Fix screenshot capture on eMAG"
- ✅ "Update README with troubleshooting tips"
- ❌ "fix bug"
- ❌ "update"

## Adding New Platforms

To add support for a new shopping platform:

1. Create `agent/platforms/newplatform.py`
2. Implement the platform class:
   ```python
   class NewPlatform:
       def __init__(self, browser_manager, gpt_agent):
           self.name = "NewPlatform"
           # ...
       
       async def search_and_analyze(self, query, part):
           # Implementation
           pass
   ```
3. Add configuration to `config.py`:
   ```python
   PLATFORMS = {
       "newplatform": {
           "name": "NewPlatform",
           "url": "https://www.example.com",
           "search_url": "https://www.example.com/search?q={query}",
           "enabled": True
       }
   }
   ```
4. Update `agent/shopping_agent.py` to include the new platform
5. Test thoroughly with multiple parts
6. Update README.md with platform details

## Questions?

- Open an [Issue](https://github.com/kazgool/rc-tank-shopping-agent/issues)
- Check existing documentation
- Review the code comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
