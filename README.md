# LeaseWatch Python Project

**Automated Apartment Pricing Tracker for Camden Dunwoody & Perimeter Gardens**

> "Stop hunting for deals. Start watching them."

Track live floor plan pricing daily using Playwright and cloud automation with **zero manual work**.

---

## 📌 Overview

**LeaseWatch** is a Python-based backend project that monitors apartment pricing daily for luxury apartment communities. It uses **Playwright** to scrape dynamic floor plan pricing and outputs logs or reports for 1B/1B and 2B/2B units.

**Current Target Properties:**
- **Camden Dunwoody**
- **The Columns at Lake Ridge**
- **Drift Dunwoody**

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.13+ |
| Headless Browser | Playwright |
| Web Framework | aiohttp (optional server) |
| Data Processing | Pydantic |
| Storage | Local JSON |
| Logging | Python logging |

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Python Script    │
│   or HTTP Server   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Playwright Scrapers │
│ - Camden           │
│ - Columns          │
│ - Drift            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Data Processing     │
│ & Report Generation │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Local JSON Storage  │
└─────────────────────┘
```

---

## 🚀 Installation

### Prerequisites
- Python 3.13 or higher
- pip package manager

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lebjawi/LeaseWatch.git
   cd LeaseWatch
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**
   ```bash
   python -m playwright install chromium
   ```

---

## � Usage

### Command Line Interface

**Run once (scrape all properties):**
```bash
python main.py
```

**Start HTTP Server:**
```bash
python server.py
```

### HTTP API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/health` | Health check |
| POST | `/scrape` | Trigger scraping |
| GET | `/data` | Get latest data |
| GET | `/report` | Get reports |
| GET | `/dates` | Available dates |
| GET | `/history` | Property history |

### Example API Calls

```bash
# Health check
curl http://localhost:8000/health

# Trigger scraping
curl -X POST http://localhost:8000/scrape

# Get latest data
curl http://localhost:8000/data

# Get daily report
curl http://localhost:8000/report?type=daily

# Get property comparison
curl http://localhost:8000/report?type=comparison

# Get property history
curl http://localhost:8000/history?property=Camden%20Dunwoody&days=30
```

---

## 📊 Sample Output

```
🏡 LeaseWatch - Starting apartment pricing tracker...
📅 Date: 2025-08-02T10:30:00

🔍 Phase 1: Data Collection
==================================================
🏢 Scraping Camden Dunwoody...
✅ Camden Dunwoody scraping completed: 12 floor plans found

🏢 Scraping The Columns at Lake Ridge...
✅ The Columns at Lake Ridge scraping completed: 8 floor plans found

🏢 Scraping Drift Dunwoody...
✅ Drift Dunwoody scraping completed: 6 floor plans found

📊 DAILY SUMMARY
==================================================
📅 Date: 2025-08-02
🏢 Properties Scraped: 3
📋 Total Floor Plans: 26
💰 Price Range: $1,400 - $3,200
💵 Average Price: $2,150

🏠 Properties:
   • Camden Dunwoody: 12 floor plans
   • The Columns at Lake Ridge: 8 floor plans
   • Drift Dunwoody: 6 floor plans
```

---

## 📁 Project Structure

```
LeaseWatch/
├── main.py                 # Main application entry point
├── server.py              # HTTP server (optional)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/                 # Local data storage
│   ├── daily/           # Daily scraped data
│   ├── reports/         # Generated reports
│   └── raw/             # Raw debug data
└── src/
    ├── scrapers/        # Web scrapers
    │   ├── camden.py
    │   ├── columns.py
    │   └── drift.py
    ├── services/        # Business logic
    │   ├── storage.py
    │   └── report.py
    ├── types/           # Data models
    │   └── types.py
    └── utils/           # Utilities
        ├── data_processor.py
        ├── report_generator.py
        └── logger.py
```

---

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file for customization:

```env
LEASEWATCH_DATA_DIR=data
LEASEWATCH_LOG_LEVEL=INFO
LEASEWATCH_SERVER_PORT=8000
LEASEWATCH_SERVER_HOST=localhost
```

### Customizing Scrapers

To add new properties, create a new scraper in `src/scrapers/` following the pattern:

```python
async def scrape_new_property() -> List[FloorPlan]:
    # Your scraping logic here
    pass
```

Then add it to `main.py` in the data collection phase.

---

## 📈 Reports Available

1. **Daily Summary** - Overview of all scraped data
2. **Property Comparison** - Compare properties by price and value
3. **Bedroom Analysis** - Analysis by bedroom count
4. **Availability Report** - Current availability status
5. **Executive Summary** - Key metrics and KPIs

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🐛 Troubleshooting

### Common Issues

**Playwright browser not found:**
```bash
python -m playwright install chromium
```

**Permission errors:**
```bash
chmod +x main.py
```

**Import errors:**
```bash
# Make sure you're in the project directory and virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**No data returned:**
- Check if the websites are accessible
- Verify the scraper selectors are still valid
- Check the logs for specific error messages

### Debug Mode

Run with debug logging:
```python
# In main.py, change logger level
logger.setLevel(logging.DEBUG)
```

---

## 📞 Support

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/lebjawi/LeaseWatch/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/lebjawi/LeaseWatch/wiki)

---

**Happy apartment hunting! 🏠✨**
+-----------+------------+
            |
            v
+------------------------+
| Data Layer             |
| - Console Logs         |
| - JSON File (local)    |
| - Optional DB (future) |
+-----------+------------+
            |
            v
+------------------------+
| Report/Delivery Layer  |
| - Email                |
| - Webhook              |
+------------------------+
```

---

## 📁 Project Structure

```
leasewatch/
├── scrapers/
│   ├── camden.js
│   └── perimeter.js
├── services/
│   ├── report.js
│   └── storage.js
├── utils/
│   └── logger.js
├── data/
│   └── prices.json
├── index.js
├── package.json
├── render.yaml
└── README.md
---

## 🚀 Development Roadmap

### 🟢 Phase 1 – Open Pages Daily (MVP)
**Goal:** Launch Puppeteer, navigate to each target apartment's main floor plan page.

- [x] Set up Puppeteer headless browser
- [ ] Navigate to target sites:
  - **Camden Dunwoody:** https://www.camdenliving.com/apartments/dunwoody-ga/camden-dunwoody/available-apartments
  - **Perimeter Gardens:** https://www.perimetergardens.com/interactivepropertymap
- [ ] Log success/failure
- [ ] Deploy to Render with daily cron job

### 🟡 Phase 2 – Extract Floor Plans & Prices
**Goal:** Scrape all 1B/1B and 2B/2B prices to console

- [ ] Parse floor plans on each site
- [ ] Filter by bed/bath configuration
- [ ] Extract plan name, price, and availability
- [ ] Output structured logs in console
- [ ] Save to `data/prices.json`

### 🟣 Phase 3 – Generate & Deliver Reports
**Goal:** Automate reporting + delivery

- [ ] Format results into structured reports (JSON/CSV)
- [ ] Choose delivery method:
  - [ ] Send email (SendGrid integration)
  - [ ] Save to cloud folder (Dropbox, Google Drive API)
  - [ ] Optional: webhook/Slack/Discord
- [ ] Add timestamps to reports
- [ ] Optional: Create historical log file

---

## 🛠️ Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/leasewatch.git
   cd leasewatch
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the script locally:**
   ```bash
   node index.js
   ```

### Deployment on Render

1. Push code to GitHub
2. Log into [Render.com](https://render.com)
3. Create new "Background Worker" → Link your repo
4. Add build/run command: `node index.js`
5. Set Cron Job schedule to `@daily`

---

## 📦 Data Output Format

**Example output (Phase 2 & 3):**

```json
{
  "date": "2025-08-02T05:00:00Z",
  "camdenData": [
    {
      "name": "Dogwood",
      "beds": "1 Bed / 1 Bath",
      "price": "$1,480"
    },
    {
      "name": "Chestnut",
      "beds": "2 Bed / 2 Bath",
      "price": "$1,750"
    }
  ],
  "perimeterData": [
    {
      "name": "Concourse A2",
      "price": "$1,435",
      "availability": "Available Now"
    }
  ]
}
```

---

## � Notifications (Phase 3)

Available delivery methods:
- 💌 **Email** (SendGrid integration)
- 📤 **Webhook** to Slack/Notion/Discord
- 🧾 **Local file** dump (JSON/CSV)

---

## 🔒 Security

⚠️ **Important:** Store sensitive information using environment variables or `.env` files:
- SendGrid API keys
- Database credentials
- Webhook URLs

**Never hardcode credentials in your scripts.**

---

## 💡 Future Enhancements

- [ ] Historical price trends & visualization
- [ ] Add more apartment communities
- [ ] Rent drop alerts
- [ ] Personal dashboard UI (React + Chart.js)
- [ ] Mobile app notifications
- [ ] Price prediction algorithms

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🧠 About

Created with love and frustration by someone who refuses to get ripped off by rent hikes.

**LeaseWatch** aims to be the go-to automation tool for renters, real estate investors, and housing researchers who want **real-time, reliable** rental pricing updates.
🟢 Phase 1 – Open Pages Daily (MVP)
Goal: Launch Puppeteer, navigate to each target apartment's main floor plan page.

 Set up Puppeteer headless browser

 Navigate to:

Camden Dunwoody: https://www.camdenliving.com/apartments/dunwoody-ga/camden-dunwoody/available-apartments

Perimeter Gardens: https://www.perimetergardens.com/interactivepropertymap

 Log success/failure

 Deploy to Render with daily cron job

🟡 Phase 2 – Extract Floor Plans & Prices
Goal: Scrape all 1B/1B and 2B/2B prices to console

 Parse floor plans on each site

 Filter by bed/bath

 Extract plan name, price, and availability

 Output structured logs in console

 Save to data/prices.json

🟣 Phase 3 – Generate & Deliver Reports
Goal: Automate reporting + delivery to you

 Format results into report (JSON/CSV)

 Choose delivery method:

 Send email (e.g. via SendGrid)

 Save to cloud folder (Dropbox, Google Drive API)

 Optional: webhook/Slack/Discord

 Add timestamps to reports

 Optional: Create historical log file

🛠️ Local Development
1. Clone the repo:

git clone https://github.com/your-username/leasewatch.git
cd leasewatch
2. Install dependencies:

npm install
3. Run the script locally:

node index.js
☁️ Deploy to Render
Setup:
Push code to GitHub.

Log into Render.com

Create new “Background Worker” → Link your repo

Add this build/run command:

node index.js
Set Cron Job schedule to @daily

📦 Output Format (Phase 2 & 3)

{
  "date": "2025-08-02T05:00:00Z",
  "camdenData": [
    {
      "name": "Dogwood",
      "beds": "1 Bed / 1 Bath",
      "price": "$1,480"
    },
    {
      "name": "Chestnut",
      "beds": "2 Bed / 2 Bath",
      "price": "$1,750"
    }
  ],
  "perimeterData": [
    {
      "name": "Concourse A2",
      "price": "$1,435",
      "availability": "Available Now"
    }
  ]
}
📬 Contact / Alerts (Coming Phase 3)
You’ll be able to receive daily reports:

💌 Email (SendGrid integration)

📤 Webhook to Slack/Notion/Discord

🧾 Optional local file dump (JSON/CSV)

🔒 Security Note
Make sure to store secrets (like SendGrid API keys) using .env or environment variables on Render — never hardcode credentials in your scripts.

💡 Future Features
 Historical price trends & visualization

 Add more apartment communities

 Rent drop alerts

 Personal dashboard UI (React + Chart.js)

🧠 Credits
Created with love and frustration by someone who refuses to get ripped off by rent hikes.

📜 License
MIT License — open source and open for contribution.

---

Let me know if you'd like me to create the actual project boilerplate as a zip or GitHub-ready repo structure next.
