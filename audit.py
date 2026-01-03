import os
import pandas as pd

INPUT_FILE = "data/sample_shipments.csv"
OUTPUT_FILE = "output/audit_report.csv"


def audit_shipments(input_file: str = INPUT_FILE, output_file: str = OUTPUT_FILE) -> None:
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    df = pd.read_csv(input_file)

    required_cols = {"order_id", "weight_kg", "declared_weight_kg", "delivery_days", "sla_days"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["weight_issue"] = df["weight_kg"] != df["declared_weight_kg"]
    df["sla_issue"] = df["delivery_days"] > df["sla_days"]
    df["audit_status"] = df.apply(
        lambda row: "ISSUE" if row["weight_issue"] or row["sla_issue"] else "OK",
        axis=1,
    )

    issues_df = df[df["audit_status"] == "ISSUE"].copy()
    issues_df.to_csv(output_file, index=False)

    print("✅ Audit completed.")
    print(f"⚠️ Issues found: {len(issues_df)}")
    print(f"📄 Report saved to: {output_file}")


if __name__ == "__main__":
    audit_shipments()
