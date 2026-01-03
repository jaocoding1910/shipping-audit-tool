# Shipping Audit Tool

A Python tool to audit shipping data and detect operational inconsistencies (weight mismatch and SLA violations).

## ✅ Features
- Reads shipment data from a CSV file
- Flags weight discrepancies (actual vs. declared)
- Flags SLA violations (delivery time > SLA)
- Exports a report with only the problematic rows

## 🧰 Tech Stack
- Python
- Pandas

## 📂 Project Structure
md

## ▶️ How to Run

```bash
pip install -r requirements.txt
python audit.py


---

### PASSO 1.3 — Adicionar a saída gerada
👉 Abaixo disso, cole:

```md
## 📊 Output
Generates:
- `output/audit_report.csv` (only rows with issues)

## 🚀 Next Improvements
- Configurable rules and thresholds
- Summary metrics (issue rate, SLA compliance)
- Support for multiple input files

