# Garmin Running Automation

This project fetches running activity data from Garmin Connect, analyzes key metrics, and optionally sends summary reports by email.

---

## 📂 Project Structure

garmin_project/
  ├─ src/
  │    ├─ fetch_garmin_activities.py   # Login & fetch activities from Garmin Connect
  │    ├─ analyze_activity.py          # Analyze and visualize activity data
  │    └─ mailer.py                    # Send summary reports via email
  │
  ├─ data/
  │    ├─ raw/                         # Raw activity exports (not tracked by Git)
  │    └─ processed/                   # Cleaned / preprocessed data
  │
  ├─ .gitignore                        # Ignore venv, data, caches, etc.
  ├─ requirements.txt                  # Python dependencies
  └─ README.md                         # This file

---

## 🔧 Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# or Git Bash
source .venv/Scripts/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Fetching activities from Garmin

```python
from src.fetch_garmin_activities import fetch_recent_activities

df = fetch_recent_activities(days=30)
df.to_csv("data/raw/activities_last_30_days.csv", index=False)
```

## 📊 Analyzing activities

```python
from src.analyze_activity import run_analysis

run_analysis(input_path="data/raw/activities_last_30_days.csv",
             output_dir="data/processed")
```

## ✉️ Sending reports by email

```python
from src.mailer import send_daily_report

send_daily_report(
    summary_path="data/processed/daily_summary.csv",
    to_address="your.address@example.com"
)
```

## 📝 Notes

Do not commit personal Garmin data or credentials.
Use a .env file or environment variables for usernames, passwords, and API keys.