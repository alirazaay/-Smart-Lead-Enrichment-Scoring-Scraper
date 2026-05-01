# 🎯 Smart Lead Enrichment & Scoring Tool

AI-powered lead generation tool that automatically enriches company data and scores leads based on business value.

Enter a company name or website → get a complete, scored lead profile ready for sales outreach.

---

## 🚀 Features

- **Email Extraction** — Automatically scrapes company websites for contact emails using regex pattern matching
- **Company Enrichment** — Fetches industry, size, and location data via Hunter.io API (with built-in fallback dataset)
- **Smart Scoring** — Scores leads 0–100 based on 5 weighted business factors
- **Priority Classification** — HIGH / MEDIUM / LOW based on conversion potential
- **CSV Export** — Download lead data as CSV for import into your CRM
- **Quick Try** — Pre-loaded buttons for instant demo with well-known companies

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3 + Flask |
| **Scraping** | BeautifulSoup4 + Requests |
| **Enrichment** | Hunter.io API + 15-company fallback dataset |
| **Frontend** | Vanilla HTML / CSS / JavaScript |
| **Typography** | Inter (Google Fonts) |

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/-Smart-Lead-Enrichment-Scoring-Scraper.git
cd -Smart-Lead-Enrichment-Scoring-Scraper

# 2. Install Python dependencies
cd backend
pip install -r requirements.txt

# 3. (Optional) Configure Hunter.io API key
cp .env.example .env
# Edit .env and add your HUNTER_API_KEY
# The app works without it using the built-in fallback dataset

# 4. Run the server
python app.py
```

### Open in Browser

Navigate to **http://localhost:5000** — the app serves both the API and frontend.

---

## 🎯 Scoring Algorithm

Leads are scored from 0–100 across 5 weighted business factors:

| Factor | Max Points | What It Measures |
|--------|-----------|------------------|
| **Data Quality** | 30 | Completeness of contact and company data |
| **Industry Fit** | 25 | Match with target industries (Tech, SaaS, FinTech, etc.) |
| **Geography** | 20 | Preference for US, UK, Canada, Australia markets |
| **Company Size** | 15 | Ideal range: 100–5,000 employees (mid-market) |
| **Contact Access** | 10 | Number of available contact email addresses |

### Priority Levels

| Score | Priority | Meaning |
|-------|----------|---------|
| 70–100 | 🔥 **HIGH** | Immediate outreach recommended |
| 40–69 | ⚡ **MEDIUM** | Consider personalized outreach |
| 0–39 | 📋 **LOW** | Needs more research first |

---

## 🔌 API Reference

### `POST /api/analyze`

Analyze a company and return enriched + scored lead data.

**Request:**
```json
{
  "company": "stripe.com"
}
```

**Response:**
```json
{
  "domain": "stripe.com",
  "company_name": "Stripe, Inc.",
  "industry": "Financial Technology (FinTech)",
  "employee_count": "5000-10000",
  "location": "San Francisco, CA, USA",
  "emails": ["support@stripe.com"],
  "total_score": 92,
  "priority": "HIGH",
  "emoji": "🔥",
  "breakdown": {
    "Contact emails found": 5,
    "Company identified": 10,
    "Industry data available": 5,
    "Target industry match": 25,
    "Priority market location": 20,
    "Good company size": 10,
    "Contact email found": 5
  },
  "recommendation": "High-value lead. Prioritize immediate outreach..."
}
```

### `GET /api/health`

Health check endpoint.

---

## 💡 Business Value

This tool helps sales teams:

- **Save 15+ min per lead** — No manual research needed
- **Focus efforts** — Only reach out to high-quality, scored leads
- **Increase conversion** — Target companies with the best fit signals
- **Standardize process** — Consistent scoring across all team members

---

## 📁 Project Structure

```
├── backend/
│   ├── app.py              # Flask API server
│   ├── scraper.py           # Email scraping engine
│   ├── enrichment.py        # Company data enrichment
│   ├── scorer.py            # Lead scoring algorithm
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variable template
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── styles.css           # Dark theme CSS
│   └── app.js               # Client-side JavaScript
└── README.md
```

---

## ⚠️ Notes

- **Hunter.io API** is optional. The app includes a built-in dataset of 15 well-known companies for reliable demos.
- **Email scraping** depends on the target website's structure. Some sites may block automated requests.
- **For production use**, consider adding rate limiting, caching, and a proper database.