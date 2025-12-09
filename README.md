# Garmin Running Automation Project

This project automates the workflow of fetching running activities from Garmin Connect, processing weekly summaries, generating visualizations, and optionally emailing the weekly report.  
It is structured as a clean Python project using `src/` modules, environment-based authentication, and a well-organized data directory.

---

## 🚀 Features

- Fetch recent activity lists from Garmin Connect API  
- Retrieve detailed per-second timeseries data  
- Convert Garmin metrics into clean pandas DataFrames  
- Generate weekly running summaries (distance, pace, HR, power, TE, etc.)  
- Export summaries as CSV files  
- Produce pace × heart-rate plots  
- Automatically email the weekly report as an attachment  
- Uses a structured directory layout to keep data organized  

---

## 📂 Project Structure

```text
garmin_project/
  ├─ src/
  │    ├─ fetch_garmin_activities.py     # Fetch activity list, details, weekly summary
  │    ├─ analyze_activity.py            # Generate Pace × HR plots
  │    ├─ mailer.py                      # Email sending logic
  │    └─ __init__.py
  │
  ├─ data/
  │    ├─ raw/                           # Raw activity & timeseries data
  │    ├─ processed/                     # Cleaned and structured outputs
  │    ├─ figures/                       # Generated plots
  │    └─ exports/                       # Files prepared for emailing
  │
  ├─ .env                                # Garmin/Gmail credentials (DO NOT COMMIT)
  ├─ .gitignore
  ├─ README.md
  └─ requirements.txt
```

---

## 🔑 Environment Variables (`.env`)

Your `.env` file **must be placed under `src/.env`**.

```env
# Garmin Login
GARMIN_USERNAME=your_garmin_email
GARMIN_PASSWORD=your_garmin_password

# Mail Setup
GMAIL_ADDRESS=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
MAIL_TO=recipient@example.com
```

⚠️ Never upload `.env` to GitHub.

---

## 📦 Installation

```bash
python -m venv .venv
source .venv/Scripts/activate     # Windows PowerShell
pip install -r requirements.txt
```

---

## 📥 Fetch Activity Data

### Get list of recent activities

```python
from src.fetch_garmin_activities import fetch_activity_list

df = fetch_activity_list(days=7)
print(df.head())
```

### Fetch detailed timeseries

```python
from src.fetch_garmin_activities import fetch_activity_timeseries

df_ts = fetch_activity_timeseries(activity_id=123456789)
```

---

## 📊 Weekly Summary

```python
from src.fetch_garmin_activities import export_weekly_summary_csv

export_weekly_summary_csv(days=7)
```

Creates:

```
data/processed/weekly_summary.csv
```

Running:

```bash
python -m src.fetch_garmin_activities
```

will:

- generate summary  
- copy to `data/exports/`  
- email the report using Gmail  

---

## 📈 Pace × Heart Rate Plot

```python
from src.analyze_activity import pick_activity, make_pace_hr_plot, fetch_activity_timeseries

activity_id = pick_activity()
df_ts = fetch_activity_timeseries(activity_id)
make_pace_hr_plot(df_ts)
```

Output is saved to:

```
data/figures/pace_hr_plot.png
```

---

## ✉️ Email the Weekly Summary

```python
from src.mailer import send_weekly_csv

send_weekly_csv("data/exports/weekly_summary.csv")
```

---

## ▶️ Full Automation

```bash
python -m src.fetch_garmin_activities
```

---

## 🛡️ Notes

- `.env` must exist under `src/`  
- `data/` subfolders are ignored by Git (recommended)  
- Requires Python 3.10+  
- Gmail requires an **App Password**  

---

## 📄 License

This project is for personal use. Modify freely.
