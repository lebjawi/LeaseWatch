# 🏡 LeaseWatch

**Automated Apartment Pricing Tracker for Camden Dunwoody & Perimeter Gardens**  
Track live floor plan pricing daily using Puppeteer and cloud automation.

---

## 📌 Project Overview

**LeaseWatch** is a Node.js-based backend project that monitors apartment pricing daily for select luxury apartment communities.  
It uses **Puppeteer** to scrape dynamic floor plan pricing and outputs logs or reports for 1B/1B and 2B/2B units — so you never have to check manually again.

This MVP focuses on:
- **Camden Dunwoody**  
- **Perimeter Gardens at Georgetown**

---

## 🎯 Vision

> "Stop hunting for deals. Start watching them."

LeaseWatch aims to be the go-to automation tool for renters, real estate investors, and housing researchers who want **real-time, reliable** rental pricing updates with **zero manual work**.

---

## 🏗️ Architecture

```plaintext
+------------------------+
|   Render Cron Job      |
+-----------+------------+
            |
            v
+------------------------+
| Node.js + Puppeteer    |
+-----------+------------+
            |
            v
+------------------------+
| Scraper Logic          |
| - Camden               |
| - Perimeter Gardens    |
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
🔧 Tech Stack
Component	Tech
Backend	Node.js
Headless Browser	Puppeteer
Scheduler	Render Cron Job
Storage	Local JSON (or Supabase later)
Notification	SendGrid (Phase 3)
Logging	Console / Winston

📁 Folder Structure

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
🚀 Phased Development Plan
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
