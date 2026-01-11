from pathlib import Path
import pandas as pd
import streamlit as st

from audit import run_audit, INPUT_FILE, OUTPUT_FILE

st.set_page_config(page_title="Shipping Audit Tool", page_icon="📦", layout="wide")

# --- Custom UI (Shopee-like orange) ---
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.8rem; padding-bottom: 3rem; }
      .sh-card {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        background: linear-gradient(135deg, rgba(238,77,45,0.22), rgba(0,0,0,0.0));
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
      }
      .sh-title { font-size: 42px; font-weight: 800; margin: 0; }
      .sh-sub { opacity: 0.85; margin-top: 6px; }
      [data-testid="stSidebar"] .stButton button { border-radius: 12px; font-weight: 800; }
      [data-testid="stMetric"]{
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.03);
      }
      [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sh-card">
      <div style="display:flex;gap:14px;align-items:center;">
        <div style="font-size:34px;">📦</div>
        <div>
          <p class="sh-title">Shipping Audit Tool</p>
          <p class="sh-sub">Audit shipping CSV data for weight mismatches and SLA violations — with a clean dashboard experience.</p>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# --- Sidebar controls ---
st.sidebar.header("🧭 Controls")

uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
use_sample = st.sidebar.checkbox("Use sample dataset (repo)", value=(uploaded is None))

st.sidebar.markdown("### ⚖️ Weight tolerance")
tol = st.sidebar.slider(
    "Tolerance (kg)",
    min_value=0.0,
    max_value=2.0,
    value=0.0,
    step=0.1,
    help="If > 0, only flags weight issues when abs(weight - declared) > tolerance."
)

st.sidebar.markdown("### 🔎 Filters")
only_issues = st.sidebar.toggle("Show only issues", value=True)
include_weight = st.sidebar.toggle("Include weight mismatch", value=True)
include_sla = st.sidebar.toggle("Include SLA violation", value=True)

st.sidebar.markdown("---")
run_btn = st.sidebar.button("🚀 Run Audit", use_container_width=True)

# --- Load data ---
df = None
if use_sample:
    if Path(INPUT_FILE).exists():
        df = pd.read_csv(INPUT_FILE)
    else:
        st.error("Sample file not found. Ensure data/sample_shipments.csv exists.")
        st.stop()
else:
    if uploaded is not None:
        df = pd.read_csv(uploaded)

if df is None:
    st.info("Upload a CSV or select the sample dataset in the sidebar.")
    st.stop()

tabs = st.tabs(["📊 Overview", "📄 Data", "ℹ️ About"])
tab_overview, tab_data, tab_about = tabs

with tab_data:
    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True)

with tab_about:
    st.subheader("What this tool does")
    st.markdown(
        """
**Shipping Audit Tool** helps logistics/ops teams quickly detect:
- **Weight mismatch** between actual and declared values
- **SLA violations** where delivery time exceeds SLA

**Workflow**
1) Upload CSV (or use sample)  
2) Click **Run Audit**  
3) Review metrics + charts + issue table  
4) Download the report  
"""
    )

with tab_overview:
    st.subheader("Run & Results")

    if not run_btn:
        st.info("Click **Run Audit** in the sidebar to generate metrics, charts and reports.")
        st.stop()

    if not include_weight and not include_sla:
        st.warning("Enable at least one filter: Weight mismatch and/or SLA violation.")
        st.stop()

    audited_df, issues_df = run_audit(df, weight_tolerance_kg=tol)

    total = len(audited_df)
    total_issues = len(issues_df)
    ok = total - total_issues
    issue_rate = (total_issues / total * 100) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total rows", total)
    c2.metric("Issues", total_issues)
    c3.metric("OK", ok)
    c4.metric("Issue rate", f"{issue_rate:.1f}%")

    st.success("✅ Audit completed!")

    # Charts
    st.subheader("📈 Visual Analysis")
    weight_issues = int(issues_df["weight_issue"].sum()) if len(issues_df) else 0
    sla_issues = int(issues_df["sla_issue"].sum()) if len(issues_df) else 0

    left, right = st.columns(2)

    with left:
        st.caption("Issues by type")
        chart_df = pd.DataFrame(
            {"Issue Type": ["Weight mismatch", "SLA violation"], "Count": [weight_issues, sla_issues]}
        ).set_index("Issue Type")
        st.bar_chart(chart_df)

    with right:
        st.caption("OK vs ISSUE")
        status_df = pd.DataFrame({"Status": ["OK", "ISSUE"], "Count": [ok, total_issues]}).set_index("Status")
        st.bar_chart(status_df)

    # Apply filters to table
    table_df = audited_df.copy()

    if only_issues:
        table_df = table_df[table_df["audit_status"] == "ISSUE"].copy()

    if include_weight and not include_sla:
        table_df = table_df[table_df["weight_issue"] == True].copy()
    elif include_sla and not include_weight:
        table_df = table_df[table_df["sla_issue"] == True].copy()

    st.subheader("⚠️ Report Table")
    if len(table_df) == 0:
        st.warning("No rows match the current filters.")
    else:
        st.dataframe(table_df, use_container_width=True)

    # Save issues report locally (optional)
    Path(OUTPUT_FILE).parent.mkdir(exist_ok=True)
    issues_df.to_csv(OUTPUT_FILE, index=False)

    st.subheader("⬇️ Exports")
    colA, colB = st.columns(2)

    with colA:
        st.download_button(
            label="Download issues report (CSV)",
            data=issues_df.to_csv(index=False).encode("utf-8"),
            file_name="audit_report.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with colB:
        st.download_button(
            label="Download full audited dataset (CSV)",
            data=audited_df.to_csv(index=False).encode("utf-8"),
            file_name="audited_dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )
