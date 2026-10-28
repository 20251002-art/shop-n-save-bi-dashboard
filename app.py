import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Shop N Save | Retail BI Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Shop N Save Supermarket — Retail Sales BI Dashboard")
st.warning(
    "ACADEMIC PROJECT — SYNTHETIC DATA ONLY. "
    "These figures are simulated for demonstration and are not actual Shop N Save business results."
)

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "Shop_N_Save_Synthetic_Sales_2025.csv"
    if not file_path.exists():
        return None
    data = pd.read_csv(file_path)
    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    numeric_cols = [
        "Quantity", "Unit_Price_FJD", "Unit_Cost_FJD",
        "Revenue_FJD", "Cost_FJD", "Gross_Profit_FJD", "Profit_Margin_Pct"
    ]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data

df = load_data()
if df is None:
    st.error(
        "Dataset file not found. Upload your CSV to this GitHub repository and name it exactly "
        "`Shop_N_Save_Synthetic_Sales_2025.csv`."
    )
    st.stop()

required = ["Date", "Branch", "Category", "Product", "Quantity", "Revenue_FJD", "Gross_Profit_FJD"]
missing = [col for col in required if col not in df.columns]
if missing:
    st.error(f"The CSV is missing these required columns: {', '.join(missing)}")
    st.write("Columns found:", list(df.columns))
    st.stop()

st.sidebar.header("Dashboard filters")
branches = ["All branches"] + sorted(df["Branch"].dropna().astype(str).unique().tolist())
categories = ["All categories"] + sorted(df["Category"].dropna().astype(str).unique().tolist())
selected_branch = st.sidebar.selectbox("Choose branch", branches)
selected_category = st.sidebar.selectbox("Choose category", categories)

filtered = df.copy()
if selected_branch != "All branches":
    filtered = filtered[filtered["Branch"].astype(str) == selected_branch]
if selected_category != "All categories":
    filtered = filtered[filtered["Category"].astype(str) == selected_category]

if filtered.empty:
    st.info("No records match these filters. Please choose different filters.")
    st.stop()

revenue = filtered["Revenue_FJD"].sum()
profit = filtered["Gross_Profit_FJD"].sum()
units = filtered["Quantity"].sum()
margin = (profit / revenue * 100) if revenue else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"FJD ${revenue:,.2f}")
k2.metric("Gross Profit", f"FJD ${profit:,.2f}")
k3.metric("Units Sold", f"{units:,.0f}")
k4.metric("Gross Profit Margin", f"{margin:.1f}%")

st.caption(f"Showing {len(filtered):,} synthetic transaction records.")

chart1, chart2 = st.columns(2)
with chart1:
    monthly = filtered.dropna(subset=["Date"]).copy()
    if not monthly.empty:
        monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)
        monthly_sales = monthly.groupby("Month", as_index=False)["Revenue_FJD"].sum()
        fig = px.line(monthly_sales, x="Month", y="Revenue_FJD", markers=True,
                      title="Monthly Revenue Trend", labels={"Revenue_FJD": "Revenue (FJD)", "Month": "Month"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No valid dates available for the monthly trend.")

with chart2:
    category_sales = filtered.groupby("Category", as_index=False)["Revenue_FJD"].sum().sort_values("Revenue_FJD", ascending=False)
    fig = px.bar(category_sales, x="Category", y="Revenue_FJD", title="Revenue by Category",
                 labels={"Revenue_FJD": "Revenue (FJD)"})
    st.plotly_chart(fig, use_container_width=True)

chart3, chart4 = st.columns(2)
with chart3:
    product_sales = filtered.groupby("Product", as_index=False)["Revenue_FJD"].sum().nlargest(10, "Revenue_FJD")
    fig = px.bar(product_sales.sort_values("Revenue_FJD"), x="Revenue_FJD", y="Product", orientation="h",
                 title="Top 10 Products by Revenue", labels={"Revenue_FJD": "Revenue (FJD)"})
    st.plotly_chart(fig, use_container_width=True)

with chart4:
    if "Payment_Method" in filtered.columns:
        payment_sales = filtered.groupby("Payment_Method", as_index=False)["Revenue_FJD"].sum()
        fig = px.pie(payment_sales, names="Payment_Method", values="Revenue_FJD",
                     title="Revenue by Payment Method")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Payment_Method column not found in the dataset.")

chart5, chart6 = st.columns(2)
with chart5:
    fig = px.scatter(filtered, x="Quantity", y="Revenue_FJD", color="Category",
                     title="Quantity vs Revenue", labels={"Revenue_FJD": "Revenue (FJD)"})
    st.plotly_chart(fig, use_container_width=True)

with chart6:
    if "Gross_Profit_FJD" in filtered.columns:
        profit_by_category = filtered.groupby("Category", as_index=False)["Gross_Profit_FJD"].sum().sort_values("Gross_Profit_FJD", ascending=False)
        fig = px.bar(profit_by_category, x="Category", y="Gross_Profit_FJD",
                     title="Gross Profit by Category", labels={"Gross_Profit_FJD": "Gross Profit (FJD)"})
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Filtered data preview")
st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="shop_n_save_filtered_synthetic_sales.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("Prepared for academic demonstration. All transaction data and results shown here are synthetic.")
