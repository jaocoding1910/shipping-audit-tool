<<<<<<< HEAD
# 📦 Shipping Audit Tool

A data auditing dashboard built with **Python + Streamlit** to detect operational issues in shipping data, such as **weight mismatches** and **SLA violations**.

This project simulates a real-world logistics auditing scenario commonly found in **e-commerce, fulfillment centers, and last-mile operations**.

---

## 🚀 Why this project?

Logistics operations handle thousands of shipments daily.  
Small inconsistencies can generate **financial losses, SLA penalties, and customer dissatisfaction**.

This tool automates the audit process and provides:
- Immediate visibility of issues
- Clear operational metrics
- Exportable reports for decision-making

---

## 🧠 What the tool does

✔ Audits CSV shipment data  
✔ Detects weight mismatches (actual × declared)  
✔ Detects SLA violations (delivery time × SLA)  
✔ Displays KPIs and visual charts  
✔ Allows filtering and tolerance configuration  
✔ Exports clean audit reports  

---

## 🖥️ Application Preview

The app includes:
- Interactive dashboard (Streamlit)
- File upload or sample dataset
- Filters and audit rules
- Visual analytics
- CSV export

> Designed with a **clean, professional UI inspired by modern e-commerce dashboards**.

---

## 📊 Metrics & Visuals

- Total shipments
- Issues detected
- OK vs Issue rate
- Issue breakdown by type (Weight / SLA)

---

## 🧰 Tech Stack

- Python
- Pandas
- Streamlit
- CSV-b
=======
# Shipping Audit Tool

A Python tool to audit shipping data and detect operational inconsistencies such as weight mismatches and SLA violations.

## ✅ Features
- Reads shipment data from a CSV file
- Flags weight discrepancies (actual vs. declared)
- Flags SLA violations (delivery time > SLA)
- Exports a report with only the problematic rows

## 🧰 Tech Stack
- Python
- Pandas

## 📁 Project Structure
```
data/             # sample input dataset
output/           # generated reports
audit.py          # main script
requirements.txt  # dependencies
.gitignore        # ignored files
```
>>>>>>> 8241082b7fbd78dd8db8d5faf636f848a689e4db
