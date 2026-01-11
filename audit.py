from __future__ import annotations
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "data" / "sample_shipments.csv"
OUTPUT_FILE = BASE_DIR / "output" / "audit_report.csv"

REQUIRED_COLUMNS = {
    "order_id",
    "weight_kg",
    "declared_weight_kg",
    "delivery_days",
    "sla_days",
}


def validate_schema(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def run_audit(df: pd.DataFrame, weight_tolerance_kg: float = 0.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    validate_schema(df)

    audited = df.copy()

    audited["weight_diff_kg"] = (audited["weight_kg"] - audited["declared_weight_kg"]).abs()

    if weight_tolerance_kg > 0:
        audited["weight_issue"] = audited["weight_diff_kg"] > weight_tolerance_kg
    else:
        audited["weight_issue"] = audited["weight_kg"] != audited["declared_weight_kg"]

    audited["sla_issue"] = audited["delivery_days"] > audited["sla_days"]

    audited["audit_status"] = audited.apply(
        lambda r: "ISSUE" if (r["weight_issue"] or r["sla_issue"]) else "OK",
        axis=1,
    )

    issues = audited[audited["audit_status"] == "ISSUE"].copy()
    return audited, issues


def audit_shipments(input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE, weight_tolerance_kg: float = 0.0) -> Path:
    input_file = Path(input_file)
    output_file = Path(output_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file.parent.mkdir(exist_ok=True)

    df = pd.read_csv(input_file)
    _, issues = run_audit(df, weight_tolerance_kg=weight_tolerance_kg)
    issues.to_csv(output_file, index=False)

    return output_file


if __name__ == "__main__":
    path = audit_shipments()
    print("✅ Audit completed.")
    print(f"📄 Report saved to: {path}")
