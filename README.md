# SG HDB Price Analyzer

A real-time HDB resale price analysis tool powered by data.gov.sg, Bright Data, and a local Ollama LLM.

## Features

- Real-time price analysis against Singapore's HDB resale market
- AI-powered verdicts (Underpriced / Fair / Overpriced) via Ollama llama3.2
- Interactive AI chatbot for HDB market questions
- Live scraping via Bright Data + ActionBook
- Historical data from data.gov.sg

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **LLM:** Ollama (llama3.2) — runs locally
- **Scraping:** Bright Data Scraping Browser + ActionBook
- **Data:** data.gov.sg Resale Flat Prices API + CSV
- **Session Management:** Acontext

## Project Structure
```
AgentForge/
├── app.py # Flask app + routes
├── main.py # CLI entry point
├── templates/
│ └── index.html # Frontend UI
├── agent/
│ ├── analyzer.py # Price analysis + Ollama
│ ├── browser.py # Bright Data + ActionBook scraper
│ ├── scraper.py # Playwright scraper
│ └── context.py # Acontext session management
├── data/
│ └── resale_prices.csv # Downloaded from data.gov.sg (not committed)
├── .env # Environment variables (not committed)
├── .gitignore
└── requirements.txt
```
## Setup

### 1. Clone the repo
```
git clone https://github.com/yourusername/AgentForge.git
cd AgentForge
```
2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate      # Windows
```
3. Install dependencies

```
pip install -r requirements.txt
```
4. Set up .env

```
BRIGHT_DATA_WS=wss://brd-customer-xxx-zone-brower_hdb:password@brd.superproxy.io:9222
BRIGHT_DATA_AUTH=brd-customer-xxx-zone-brower_hdb:password
ACTIONBOOK_PATH=C:\Users\yourname\AppData\Roaming\npm\actionbook.ps1
ACONTEXT_API_KEY=your_acontext_api_key
DATA_GOV_API_KEY=your_data_gov_api_key
```
5. Download HDB resale data

Download the CSV from data.gov.sg and place it at:

```
data/resale_prices.csv

Link: https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view
```
6. Install and start Ollama

```
# Download from https://ollama.com
ollama pull llama3.2
```
7. Run the app

```
python app.py
```
Visit http://localhost:5000
Usage

    Select a Town and Flat Type

    Enter a listing price

    Click Run Analysis for an AI-powered verdict

    Use the chat assistant to ask anything about the HDB market

Disclaimer

Not financial advice. For informational purposes only.
Data sourced from data.gov.sg under the Singapore Open Data Licence.
