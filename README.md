# GIndexChecker

GIndexChecker is a Python-based tool for massive analysis of domain and URL indexing in Google. It is designed for webmasters, SEOs, and anyone interested in monitoring the visibility of their own or third-party websites.


## Features

- **Smart domain filtering:** Paste any text containing domains (e.g., website content or a messy list), and the program will automatically extract all domains, remove duplicates, and discard unrelated text.
- **Indexing analysis:** Uses the Google Custom Search API to check the number of indexed URLs for each domain.
- **Results export:** Export results as CSV or copy them directly to the clipboard.
- **Manual review:** Click any domain in the results list to open a `site:domain.com` search in your browser for manual verification.
- **Multiple API key support:** Configure and use several API keys to ensure the tool works continuously.
- **Graphical interface:** Intuitive design based on Tkinter for easy use.
- **Cross-platform:** Developed in Python, compatible with Windows, Linux, and macOS (tested on Windows and Ubuntu).

## Requirements

- Python 3.7 or higher.
- Dependencies listed in `requirements.txt`.
- On Linux, ensure the package `python3-tk` is installed for Tkinter support.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/TaoPaiAI/gindexchecker.git
   cd gindexchecker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** On Linux, you may need to install Tkinter separately:
   > ```bash
   > sudo apt-get install python3-tk
   > ```

## Usage

1. Run the main script:
   ```bash
   python src/main.py
   ```

2. Configure your API keys and CX in the configuration menu:
   - **API Keys:** Go to "Settings > API Keys" and follow the steps to add your Google Custom Search keys.
   - **CX Key:** Go to "Settings > CX" and follow the steps to add your CX key.

3. Paste any list containing domains (even if it has other text) into the main input box. The program will automatically extract unique domains and discard the rest.

4. Click **Analyze Domains**. The tool will use the Google API to retrieve the number of indexed URLs per domain. Results appear on screen, and you can click any domain to open a `site:` search in Google for manual verification.

5. Export results to CSV or copy domains to the clipboard, categorized by their indexing level.

## Note

Indexing data depends on the Google API and may not be accurate in all cases. For greater precision, we recommend checking results manually.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Developed by [TaoPaiAI](https://github.com/TaoPaiAI).
