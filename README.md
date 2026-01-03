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
