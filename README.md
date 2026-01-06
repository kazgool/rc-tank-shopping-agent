# 🛒 RC Tank Shopping Agent

**AI-Powered Shopping Automation for RC Tank Parts**

An intelligent Python application that uses Playwright for web automation and GPT-4 Vision for smart product matching. Automatically searches for RC tank parts across Amazon, eMAG, and Temu, analyzes products, and generates comprehensive shopping reports.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## ✨ Features

- 🤖 **AI-Powered Product Matching**: Uses GPT-4 Vision to analyze product pages and match specifications
- 🌐 **Multi-Platform Support**: Searches Amazon, eMAG, and Temu simultaneously
- 🧠 **Smart Search Query Generation**: GPT-4 optimizes search queries for better results
- 📊 **Comprehensive Reports**: Generates detailed comparison reports with pricing and specifications
- 🖼️ **Visual Documentation**: Captures screenshots at every step for verification
- 🎯 **Human-Like Behavior**: Random delays and natural interactions to avoid detection
- 🔒 **Secure Configuration**: Environment-based credential management
- 🚀 **Beginner-Friendly**: Simple CLI interface with step-by-step setup

## 📋 Prerequisites

- **Python 3.9 or higher** ([Download Python](https://www.python.org/downloads/))
- **OpenAI API Key** ([Get API Key](https://platform.openai.com/api-keys))
- **Internet Connection**
- **Operating System**: Windows, macOS, or Linux

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/kazgool/rc-tank-shopping-agent.git
cd rc-tank-shopping-agent
```

### 2. Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

### 5. Run Setup Wizard

```bash
python main.py --setup
```

The setup wizard will:
- Create a `.env` file from the template
- Guide you through API key configuration
- Verify all dependencies are installed

### 6. Configure Your API Key

Open the `.env` file in your text editor and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your_actual_api_key_here
```

**Important**: Keep your API key secret! Never commit it to version control.

### 7. Run the Shopping Agent

```bash
python main.py --shop
```

The agent will:
1. Load the parts list from `data/parts_list.csv`
2. Search each part across all enabled platforms
3. Use AI to analyze and match products
4. Generate a comprehensive report
5. Save screenshots and logs

## 📖 Usage

### Basic Commands

```bash
# Run initial setup
python main.py --setup

# Search for parts (default: data/parts_list.csv)
python main.py --shop

# Use a custom parts file
python main.py --shop --file my_custom_parts.json

# View the latest report
python main.py --report

# Add items to cart automatically (use with caution!)
python main.py --shop --add-to-cart
```

### Using Custom Parts Lists

#### CSV Format

Create a CSV file with this structure:

```csv
part_name,category,voltage,rpm,torque,size,quantity,notes
DC Motor 12V,Motors,12V,300RPM,2Nm,40mm,2,Main drive motors
Servo Motor,Motors,6V,0.12s/60°,1.8kg-cm,23mm,2,Gun control
```

#### JSON Format

Create a JSON file with this structure:

```json
[
  {
    "name": "DC Motor 12V",
    "category": "Motors",
    "specs": {
      "voltage": "12V",
      "rpm": "300RPM",
      "torque": "2Nm"
    },
    "notes": "Main drive motors"
  }
]
```

## ⚙️ Configuration

### Environment Variables

Edit the `.env` file to configure the agent:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=your_api_key_here

# Browser Configuration
HEADLESS_MODE=False  # Set to True to run without visible browser

# Rate Limiting (seconds)
MIN_DELAY_BETWEEN_ACTIONS=2
MAX_DELAY_BETWEEN_ACTIONS=5

# Search Configuration
MAX_PRODUCTS_TO_ANALYZE=5

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Optional: Platform Login (leave empty to search without login)
AMAZON_EMAIL=
AMAZON_PASSWORD=
EMAG_EMAIL=
EMAG_PASSWORD=
TEMU_EMAIL=
TEMU_PASSWORD=
```

### Platform Configuration

You can enable/disable platforms in `config.py`:

```python
PLATFORMS = {
    "amazon": {"enabled": True, ...},
    "emag": {"enabled": True, ...},
    "temu": {"enabled": True, ...}
}
```

## 📁 Project Structure

```
rc-tank-shopping-agent/
├── agent/                      # Core agent modules
│   ├── __init__.py
│   ├── browser.py             # Playwright browser management
│   ├── gpt_vision.py          # GPT-4 Vision integration
│   ├── shopping_agent.py      # Main shopping logic
│   └── platforms/             # Platform-specific implementations
│       ├── __init__.py
│       ├── amazon.py
│       ├── emag.py
│       └── temu.py
├── data/                       # Parts lists
│   ├── parts_list.csv         # Example CSV format
│   └── parts_list.json        # Example JSON format
├── output/                     # Generated outputs
│   ├── screenshots/           # Browser screenshots
│   ├── reports/               # Shopping reports
│   └── logs/                  # Application logs
├── .vscode/                    # VS Code configuration
│   ├── launch.json            # Debug configurations
│   ├── settings.json          # Editor settings
│   └── extensions.json        # Recommended extensions
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── config.py                  # Configuration management
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔍 How It Works

1. **Load Parts List**: Reads parts from CSV or JSON file
2. **Generate Search Query**: GPT-4 optimizes the search query for each part
3. **Search Platforms**: Automated search on Amazon, eMAG, and Temu
4. **Capture Screenshots**: Takes screenshots of search results and product pages
5. **AI Analysis**: GPT-4 Vision analyzes product pages to match specifications
6. **Compare Results**: AI compares products across platforms
7. **Generate Report**: Creates detailed reports with recommendations

## 📊 Output Files

### Reports

Located in `output/reports/`:
- `shopping_report_TIMESTAMP.json` - Structured data
- `shopping_report_TIMESTAMP.txt` - Human-readable format

Example report content:
```
★ BEST MATCH: Amazon
  Price: $12.99
  Confidence: 0.95
  Reasoning: Exact specifications match, competitive price
```

### Screenshots

Located in `output/screenshots/`:
- Search result pages
- Product detail pages
- Cart/wishlist confirmations
- Error states

### Logs

Located in `output/logs/`:
- `shopping_agent.log` - Detailed execution logs
- Includes timestamps, levels, and full stack traces

## 🐛 Troubleshooting

### API Key Issues

**Problem**: `Configuration error: OPENAI_API_KEY is not set`

**Solution**: 
1. Make sure you created the `.env` file
2. Add your API key: `OPENAI_API_KEY=sk-your-key`
3. Restart the application

### Browser Not Found

**Problem**: `Playwright browser not installed`

**Solution**: 
```bash
playwright install chromium
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'playwright'`

**Solution**: 
```bash
pip install -r requirements.txt
```

### Slow Performance

**Problem**: Agent is running very slowly

**Solutions**:
- Reduce `MAX_PRODUCTS_TO_ANALYZE` in `.env`
- Increase `MIN_DELAY_BETWEEN_ACTIONS` for better reliability
- Disable platforms you don't need in `config.py`

### Platform-Specific Issues

**Problem**: Can't find products on a specific platform

**Solutions**:
- The platform may have changed their layout
- Check `output/screenshots/` to see what the agent sees
- Update selectors in `agent/platforms/[platform].py`
- Check `output/logs/shopping_agent.log` for errors

## 🔒 Security Best Practices

- ✅ Never commit your `.env` file
- ✅ Use environment variables for all secrets
- ✅ Keep your OpenAI API key private
- ✅ Review the `.gitignore` file
- ✅ Rotate API keys regularly
- ❌ Don't share screenshots that contain personal information

## 🛠️ Development

### VS Code Setup

1. Install recommended extensions (prompted on first open)
2. Use the debug configurations in Run & Debug panel:
   - "Python: Shopping Agent (Setup)"
   - "Python: Shopping Agent (Run)"
   - "Python: View Report"

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

### Code Style

This project follows PEP 8 with some modifications:
- Line length: 120 characters
- Formatter: Black
- Linter: Flake8

```bash
# Format code
black .

# Lint code
flake8 .
```

## 📝 Extending the Agent

### Adding a New Platform

1. Create `agent/platforms/newplatform.py`
2. Implement the platform class with `search_and_analyze` method
3. Add configuration to `config.py`
4. Test thoroughly with screenshots

### Adding Custom Part Fields

1. Add columns to your CSV or fields to your JSON
2. The agent automatically includes them in specifications
3. GPT-4 will consider them during matching

## 💡 Tips & Best Practices

- **Start Small**: Test with 2-3 parts before running a full list
- **Review Screenshots**: Check `output/screenshots/` to verify agent behavior
- **Monitor Logs**: Use `tail -f output/logs/shopping_agent.log` to watch in real-time
- **Adjust Delays**: Increase delays if you're getting blocked
- **Headless Mode**: Use `HEADLESS_MODE=True` for faster execution after testing
- **API Costs**: Be mindful of OpenAI API costs, especially with large parts lists

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 Vision API
- Playwright team for excellent browser automation
- RC hobbyist community for inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kazgool/rc-tank-shopping-agent/issues)
- **Documentation**: This README and inline code comments
- **Logs**: Check `output/logs/shopping_agent.log` for detailed information

## ⚠️ Disclaimer

This tool is for educational and personal use. Please:
- Respect website terms of service
- Don't abuse rate limits
- Use reasonable delays between requests
- Review and comply with each platform's automation policies

---

**Happy Shopping! 🛒🤖**
