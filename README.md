# LetsCrawl

**A simple tool for collecting structured content from websites for research and analysis.**

Perfect for researchers, journalists, analysts, or anyone who needs to gather information from multiple web sources regularly.

---

## What LetsCrawl Does

LetsCrawl helps you automatically collect information from websites and turn it into organized spreadsheets or data files. Instead of manually copying and pasting from websites, you can:

- 📰 **Collect news articles** from multiple news sites in one go
- 📡 **Discover RSS feeds** from websites you follow
- 🏪 **Gather product information** from online stores
- 📊 **Export results** to Excel-compatible CSV or JSON files

**Best of all**: You configure it once, then run it whenever you need fresh data.

---

## Who This Is For

LetsCrawl is designed for **non-technical users** who need to:

- Monitor news from multiple publications
- Track articles on specific topics
- Build datasets for research projects
- Collect structured data from websites regularly
- Archive web content over time

**You don't need to know how to code** to use LetsCrawl effectively.

---

## Quick Start

### 1. Installation

LetsCrawl requires Python 3.12 or later. If you don't have Python installed, you can download it from [python.org](https://www.python.org/downloads/).

Once Python is installed, open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
pip install letscrawl
```

Or install from the source code:

```bash
git clone https://github.com/yourusername/letscrawl.git
cd letscrawl
pip install -r requirements.txt
```

### 2. Set Up Your API Key

LetsCrawl uses AI (Groq/LLaMA) to understand and extract structured data from web pages. You'll need a free API key:

1. Go to [GroqConsole](https://console.groq.com/)
2. Sign up for a free account
3. Create a new API key
4. Copy your API key

Create a file named `.env` in the letsCrawl directory and add:

```bash
GROQ_API_KEY=your_api_key_here
```

**Important**: Keep your API key private. Don't share the `.env` file or commit it to version control.

### 3. Run Your First Crawl

Try the built-in news scraping configuration:

```bash
python main.py --config news
```

This will collect articles from several African news sites and save them to:
- `items.csv` – All collected articles
- `complete_items.csv` – Only articles with complete information

Open `items.csv` in Excel, Google Sheets, or any spreadsheet application to view your results!

---

## Using LetsCrawl

### Available Configurations

LetsCrawl comes with several pre-built configurations for common tasks:

| Configuration | What It Does | How to Use |
|--------------|--------------|-------------|
| `news` | Collects news articles from African news sites | `python main.py --config news` |
| `rss` | Discovers RSS/Atom feed URLs from websites | `python main.py --config rss --urls https://cnn.com https://nytimes.com` |
| `dental` | Scrapes dental clinic listings (example) | `python main.py --config dental` |
| `etsy` | Collects product information from Etsy | `python main.py --config etsy` |

### Customizing Crawls

#### Option 1: Modify Existing Configurations

You can customize how LetsCrawl works by editing configuration files:

1. Open `config.py` in a text editor
2. Find the configuration you want to modify
3. Change settings like:
   - `SITES`: Add or remove websites to crawl
   - `REQUIRED_KEYS`: What information to collect (title, date, author, etc.)
   - `MAX_PAGES`: How many pages to crawl
   - `DELAY_BETWEEN_PAGES`: How long to wait between requests (be respectful!)

#### Option 2: Create Your Own Configuration

For more advanced users, you can create completely custom configurations. See [Advanced Configuration](#advanced-configuration) below.

### Common Options

```bash
# List all available configurations
python main.py --list

# Crawl with translation (translate content to French)
python main.py --config news --translate --target-language fr

# Crawl specific RSS feeds
python main.py --config rss --urls https://cnn.com https://bbc.com
```

---

## Understanding Your Results

### Output Files

After running LetsCrawl, you'll find these files:

- **`items.csv`** – All items collected (may include incomplete items)
- **`complete_items.csv`** – Only items with all required information

### CSV Columns

Your CSV files will contain columns like:

- `title` – Article or item title
- `author` – Author name (if available)
- `date_published` – When it was published
- `content` – Main text or summary
- `source_site` – Which website it came from
- `retrieved_at` – When LetsCrawl collected it

The exact columns depend on your configuration and what each website provides.

---

## Example Use Cases

### Use Case 1: Monitor News from Multiple Sources

**Scenario**: You're a researcher tracking political news across West Africa.

**Solution**:

```bash
python main.py --config news
```

This automatically collects articles from Seneweb (Senegal), The Namibian (Namibia), and New Times (Rwanda).

### Use Case 2: Build a Dataset of RSS Feeds

**Scenario**: You want to find RSS feeds from major news websites.

**Solution**:

```bash
python main.py --config rss --urls https://cnn.com https://nytimes.com https://bbc.com
```

This discovers RSS feed URLs and validates them.

### Use Case 3: Collect Product Information

**Scenario**: You're tracking prices on Etsy.

**Solution**:

```bash
python main.py --config etsy
```

This collects product titles, prices, and descriptions.

### Use Case 4: Translate Content Automatically

**Scenario**: You're collecting content in French and want it translated to English.

**Solution**:

```bash
python main.py --config news --translate --target-language en
```

This extracts content AND translates it in one step!

---

## Advanced Configuration

### Creating Custom Configurations

For more control, you can create custom configurations in Python:

```python
# In config.py or my_configs.py

"my_custom_news": {
    "SITES": [
        {
            "name": "My Favorite News Site",
            "BASE_URL": "https://example.com/news",
            "CSS_SELECTOR": "article.news-story",
        }
    ],
    "REQUIRED_KEYS": ["title", "date_published", "author"],
    "OPTIONAL_KEYS": ["content", "tags"],
    "CRAWLER_CONFIG": {
        "MULTI_PAGE": True,
        "MAX_PAGES": 5,
        "DELAY_BETWEEN_PAGES": 3,  # Wait 3 seconds between pages
        "HEADLESS": True,  # Run without showing browser window
    },
    "LLM_CONFIG": {
        "PROVIDER": "groq/llama-3.3-70b-versatile",
        "EXTRACTION_TYPE": "schema",
        "INPUT_FORMAT": "markdown",
        "INSTRUCTION": """
        Extract article information including:
        - Title
        - Author
        - Publication date
        - Main content or summary
        """
    }
}
```

Then run:

```bash
python main.py --config my_custom_news
```

### Understanding Key Settings

**`CSS_SELECTOR`** – Tells LetsCrawl which parts of the page contain the information you want. Use your browser's developer tools (F12 → Inspector) to find selectors.

**`REQUIRED_KEYS`** – Fields that MUST be present for an item to be saved to `complete_items.csv`.

**`OPTIONAL_KEYS`** – Nice-to-have fields that will be saved if available.

**`MAX_PAGES`** – How many pages to crawl. Set to 1 for single-page scraping.

**`DELAY_BETWEEN_PAGES`** – How long to wait (in seconds) between requests. **Be respectful** – set to 2-5 seconds to avoid overwhelming servers.

---

## Tips for Best Results

### 1. Start Small

- Test with `MAX_PAGES: 1` first
- Verify you're getting the data you want
- Then increase `MAX_PAGES` for full crawls

### 2. Be Respectful

- Use appropriate delays between requests (2-5 seconds)
- Crawl during off-peak hours when possible
- Check if websites provide APIs or RSS feeds first

### 3. Validate Your Results

- Open `items.csv` and check if the data looks correct
- Try running the same configuration multiple times to ensure consistency
- Adjust `CSS_SELECTOR` or `INSTRUCTION` if extraction quality is poor

### 4. Handle Errors

- If LetsCrawl finds no items, check your CSS_SELECTOR
- If extraction is incomplete, try more specific instructions in `INSTRUCTION`
- Some websites may block automated tools – this is normal

### 5. Organize Your Work

- Use descriptive configuration names
- Document your data sources
- Keep track of when you crawled (the `retrieved_at` column)
- Consider setting up a schedule for regular crawls

---

## Troubleshooting

### "No items found"

- **Problem**: LetsCrawl runs but doesn't collect anything
- **Solution**: Check the `CSS_SELECTOR` – the website structure may have changed
- **Solution**: Try visiting the website manually to see if it looks different

### "API key not set"

- **Problem**: Error about `GROQ_API_KEY`
- **Solution**: Make sure your `.env` file exists and contains your API key
- **Solution**: Try restarting your terminal after creating `.env`

### "Extraction incomplete"

- **Problem**: Some items missing required fields
- **Solution**: This is normal – those items will be in `items.csv` but not `complete_items.csv`
- **Solution**: Update `REQUIRED_KEYS` to only include fields that are always present

### "Module not found"

- **Problem**: Python can't find a library
- **Solution**: Make sure you installed dependencies: `pip install -r requirements.txt`
- **Solution**: Try using a virtual environment

---

## Advanced Topics

### Output Formats

By default, LetsCrawl exports to CSV. You can also request JSON:

```bash
# CSV export (default)
python main.py --config news

# JSON export (requires code modification)
# Edit main.py to use outputs.write_json() instead of write_csv()
```

### Regular Automated Crawls

To run LetsCrawl on a schedule, use your operating system's task scheduler:

**Windows**: Task Scheduler
**Mac**: `launchctl` or cron
**Linux**: `cron`

Example cron job (runs every day at 9am):

```
0 9 * * * cd /path/to/letscrawl && /usr/bin/python3 main.py --config news
```

### Using Multiple Configurations

You can run multiple crawls sequentially:

```bash
python main.py --config news
python main.py --config rss --urls https://cnn.com
python main.py --config etsy
```

Each creates its own output files.

---

## Frequently Asked Questions

### Q: Is LetsCrawl free?

**A**: Yes! LetsCrawl itself is free. You will need a free Groq API key, which provides generous free tier access.

### Q: What websites can I crawl?

**A**: Any public website. However:
- Always check the website's Terms of Service
- Respect robots.txt files
- Be respectful with request rates
- Don't use for spam or commercial data harvesting without permission

### Q: How fast can I crawl?

**A**: This depends on:
- Website response times
- Number of pages you're crawling
- Delays between requests
- API rate limits

A typical crawl might take 1-5 minutes per website.

### Q: Can I crawl social media?

**A**: Technically yes, but:
- Most social media platforms prohibit scraping in their Terms of Service
- Consider using official APIs instead
- Be respectful and ethical

### Q: What if the website structure changes?

**A**: The AI extraction is pretty flexible and can often handle minor changes. If extraction quality drops, you may need to update the `CSS_SELECTOR` or `INSTRUCTION`.

### Q: Can I crawl password-protected content?

**A**: No. LetsCrawl only works with publicly accessible web pages.

---

## Getting Help

### Documentation

- **Configuration Guide**: Edit `config.py` to see all available options
- **Example Configurations**: Check the built-in configs for inspiration
- **Architecture Docs**: See `ARCHITECTURE.md` for technical details (for developers)

### Issues

If you encounter bugs or issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Make sure you have the latest version: `pip install --upgrade letscrawl`
3. Search existing issues at [github.com/yourusername/letscrawl/issues](https://github.com/yourusername/letscrawl/issues)
4. Create a new issue with:
   - What you were trying to do
   - What command you ran
   - What error message you saw
   - Your operating system and Python version

---

## Contributing

LetsCrawl is open to contributions! If you'd like to help improve it:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Suggestions for improvements:
- New built-in configurations for popular websites
- Better error messages
- Additional export formats
- Improved documentation

---

## License

[Specify your license here - MIT, Apache 2.0, etc.]

---

## Acknowledgments

LetsCrawl is built on top of excellent open-source tools:

- **Crawl4AI** – Web crawling and AI-powered extraction
- **Groq** – Fast AI inference for extraction
- **Pydantic** – Data validation and settings
- **Python** – Programming language

Thank you to the creators and maintainers of these amazing tools!

---

**Happy Crawling!** 🚀

If you find LetsCrawl useful, please consider giving it a ⭐ on GitHub!
