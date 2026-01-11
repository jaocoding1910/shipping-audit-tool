"""
Shipping Audit Tool (Core)
--------------------------
Core audit logic (no UI here).

Rules:
- Weight mismatch: weight_kg != declared_weight_kg
- SLA violation: delivery_days > sla_days

Outputs:
- issues_df: only problematic rows
- audited_df: full dataset with audit columns
"""

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


def run_audit(
    df: pd.DataFrame,
    weight_tolerance_kg: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run audit on a DataFrame.
    weight_tolerance_kg:
        If > 0, only flags weight issues where abs(weight - declared) > tolerance.
    """
    validate_schema(df)

    audited_df = df.copy()

    # Weight issue (supports tolerance)
    diff = (audited_df["weight_kg"] - audited_df["declared_weight_kg"]).abs()
    audited_df["weight_diff_kg"] = diff
    if weight_tolerance_kg > 0:
        audited_df["weight_issue"] = audited_df["weight_diff_kg"] > weight_tolerance_kg
    else:
        audited_df["weight_issue"] = audited_df["weight_kg"] != audited_df["declared_weight_kg"]

    # SLA issue
    audited_df["sla_issue"] = audited_df["delivery_days"] > audited_df["sla_days"]

    # Final status
    audited_df["audit_status"] = audited_df.apply(
        lambda row: "ISSUE" if row["weight_issue"] or row["sla_issue"] else "OK",
        axis=1,
    )

    issues_df = audited_df[audited_df["audit_status"] == "ISSUE"].copy()
    return audited_df, issues_df


def audit_shipments(
    input_file: Path = INPUT_FILE,
    output_file: Path = OUTPUT_FILE,
    weight_tolerance_kg: float = 0.0,
) -> Path:
    input_file = Path(input_file)
    output_file = Path(output_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_file.parent.mkdir(exist_ok=True)

    df = pd.read_csv(input_file)
    _, issues_df = run_audit(df, weight_tolerance_kg=weight_tolerance_kg)

    issues_df.to_csv(output_file, index=False)

    print("✅ Audit completed.")
    print(f"⚠️ Issues found: {len(issues_df)}")
    print(f"📄 Report saved to: {output_file}")

    return output_file


if __name__ == "__main__":
    audit_shipments()
