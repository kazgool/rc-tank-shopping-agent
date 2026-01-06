# Quick Start Guide

## 5-Minute Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browser
```bash
playwright install chromium
```

### 3. Setup Configuration
```bash
python main.py --setup
```

### 4. Add Your API Key
Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your_actual_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

### 5. Run the Shopping Agent
```bash
python main.py --shop
```

## What Happens Next?

The agent will:
1. ✅ Load parts from `data/parts_list.csv`
2. ✅ Search each part on Amazon, eMAG, and Temu
3. ✅ Use AI to analyze product pages
4. ✅ Generate a comparison report
5. ✅ Save screenshots and logs

## View Results

- **Reports**: `output/reports/shopping_report_*.txt`
- **Screenshots**: `output/screenshots/`
- **Logs**: `output/logs/shopping_agent.log`

## Common Commands

```bash
# View latest report
python main.py --report

# Use custom parts file
python main.py --shop --file my_parts.json

# Run validation
python validate.py
```

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review logs in `output/logs/` for errors
- Examine screenshots in `output/screenshots/` to see what the agent sees

## Important Notes

- ⚠️ API calls to OpenAI cost money - start with a small parts list
- ⚠️ Keep your `.env` file secret - never commit it to version control
- ⚠️ Respect website rate limits - adjust delays in `.env` if needed
- ⚠️ Review platform terms of service before using automation

## Support

- Issues: https://github.com/kazgool/rc-tank-shopping-agent/issues
- Documentation: README.md
- Logs: output/logs/shopping_agent.log
