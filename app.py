from pathlib import Path
import pandas as pd
import streamlit as st

from audit import run_audit, INPUT_FILE, OUTPUT_FILE

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Shipping Audit Tool",
    page_icon="📦",
    layout="wide",
)

# ----------------------------
# Shopee-like styling (orange)
# ----------------------------
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.8rem; padding-bottom: 3rem; }
      /* header card */
      .sh-card {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        background: linear-gradient(135deg, rgba(238,77,45,0.18), rgba(0,0,0,0.0));
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
      }
      .sh-title { font-size: 42px; font-weight: 800; margin: 0; }
      .sh-sub { opacity: 0.85; margin-top: 6px; }
      /* sidebar button spacing */
      [data-testid="stSidebar"] .stButton button {
        border-radius: 12px;
        font-weight: 700;
      }
      /* metric cards look */
      [data-testid="stMetric"]{
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.03);
      }
      /* dataframes */
      [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header
# ----------------------------
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

# ----------------------------
# Sidebar controls
# ----------------------------
st.sidebar.header("🧭 Controls")

uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
use_sample = st.sidebar.checkbox("Use sample dataset (repo)", value=(uploaded is None))

st.sidebar.markdown("### 🔎 Audit Filters")
only_issues = st.sidebar.toggle("Show only issues", value=True)
filter_weight = st.sidebar.toggle("Include weight mismatch", value=True)
filter_sla = st.sidebar.toggle("Include SLA violation", value=True)

st.sidebar.markdown("### ⚖️ Weight tolerance")
tol = st.sidebar.slider(
    "Tolerance (kg)",
    min_value=0.0,
    max_value=2.0,
    value=0.0,
    step=0.1,
    help="If > 0, only flags weight issues when abs(weight - declared) > tolerance."
)

st.sidebar.markdown("---")
run_btn = st.sidebar.button("🚀 Run Audit", use_container_width=True)

# ----------------------------
# Load data
# ----------------------------
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

# ----------------------------
# Tabs layout
# ----------------------------
tab_overview, tab_data, tab_about = st.tabs(["📊 Overview", "📄 Data", "ℹ️ About"])

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

**Why it matters:** inconsistencies can increase costs, generate claims, and impact customer experience.

**Workflow:**
1) Upload CSV (or use sample)  
2) Click **Run Audit**  
3) Review metrics + charts + issue table  
4) Download the report
"""
    )

# ----------------------------
# Run audit + render results
# ----------------------------
with tab_overview:
    st.subheader("Run & Results")

    if not run_btn:
        st.info("Click **Run Audit** in the sidebar to generate metrics, charts and reports.")
        st.stop()

    try:
        audited_df, issues_df = run_audit(df, weight_tolerance_kg=tol)

        # Apply toggles filters
        filtered = audited_df.copy()

        # If neither filter is enabled, show nothing meaningful
        if not filter_weight and not filter_sla:
            st.warning("Enable at least one filter: Weight mismatch and/or SLA violation.")
            st.stop()

        # If only issues, keep ISSUE rows
        if only_issues:
            filtered = filtered[filtered["audit_status"] == "ISSUE"].copy()

        # Filter issue types
        if filter_weight and not filter_sla:
            filtered = filtered[filtered["weight_issue"] == True].copy()
        elif filter_sla and not filter_weight:
            filtered = filtered[filtered["sla_issue"] == True].copy()
        # if both enabled -> keep as is

        # Metrics (based on full audited_df)
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

        weight_issues = int(issues_df["weight_issue"].sum()) if "weight_issue" in issues_df.columns else 0
        sla_issues = int(issues_df["sla_issue"].sum()) if "sla_issue" in issues_df.columns else 0

        chart_df = pd.DataFrame(
            {"Issue Type": ["Weight mismatch", "SLA violation"], "Count": [weight_issues, sla_issues]}
        ).set_index("Issue Type")

        left, right = st.columns(2)

        with left:
            st.caption("Issues by type")
            st.bar_chart(chart_df)

        with right:
            st.caption("OK vs ISSUE")
            status_df = pd.DataFrame({"Status": ["OK", "ISSUE"], "Count": [ok, total_issues]}).set_index("Status")
            st.bar_chart(status_df)

        # Report table
        st.subheader("⚠️ Report Table")

        if len(filtered) == 0:
            st.warning("No rows match the current filters.")
        else:
            st.dataframe(filtered, use_container_width=True)

        # Exports
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

        # Optional: save locally (nice for dev)
        Path(OUTPUT_FILE).parent.mkdir(exist_ok=True)
        issues_df.to_csv(OUTPUT_FILE, index=False)

    except Exception as e:
        st.error(f"❌ Error: {e}")
