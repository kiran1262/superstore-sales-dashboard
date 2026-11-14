import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Superstore Sales Studio", page_icon="📊", layout="wide")

# Bright, colourful dashboard styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'DM Sans', sans-serif;}
.stApp {background: linear-gradient(135deg,#f5f7ff 0%,#f8fbff 48%,#fff7fb 100%);}
.block-container {padding-top: 1.5rem; max-width: 1500px;}
.hero {background: linear-gradient(110deg,#4f46e5,#7c3aed 52%,#ec4899); padding: 27px 32px; border-radius: 22px; color: white; box-shadow: 0 12px 30px #6d5ce533; margin-bottom: 20px;}
.hero h1 {font-size: 2.1rem; margin:0; font-weight:800;}
.hero p {margin:7px 0 0; opacity:.9; font-size:1rem;}
.kpi {border-radius:18px; padding:18px 20px; color:#172554; min-height:112px; box-shadow:0 7px 22px #26345a12; border:1px solid #ffffff;}
.kpi .label {font-size:.82rem; font-weight:700; opacity:.78; text-transform:uppercase; letter-spacing:.05em;}
.kpi .value {font-size:1.8rem; font-weight:800; margin-top:6px;}
.kpi .hint {font-size:.78rem; opacity:.75; margin-top:2px;}
.section-title {font-size:1.15rem; font-weight:800; color:#24234a; margin:10px 0 8px;}
div[data-testid="stPlotlyChart"] {background:white; border-radius:16px; padding:8px; box-shadow:0 5px 18px #26345a0c;}
div[data-testid="stTabs"] button {font-weight:700;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_csv(Path(__file__).parent / "data" / "superstore_sales.csv")
    data.columns = [c.strip() for c in data.columns]
    required = ["Order Date", "Sales", "Profit", "Category", "Sub-Category", "Region", "Quantity"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        st.error("Missing required columns: " + ", ".join(missing))
        st.stop()
    data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
    for c in ["Sales", "Profit", "Quantity", "Discount"]:
        if c in data.columns:
            data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna(subset=["Order Date", "Sales", "Profit"])
    return data

st.markdown("""
<div class="hero">
  <h1>📊 Superstore Sales Studio</h1>
  <p>Explore revenue, profit, products and customer trends — all in one colourful dashboard.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎨 Dashboard controls")
    uploaded = st.file_uploader("Upload your own sales CSV", type=["csv"])
    data = load_data(uploaded)
    min_date, max_date = data["Order Date"].min().date(), data["Order Date"].max().date()
    date_range = st.date_input("📅 Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    regions = sorted(data["Region"].dropna().unique())
    categories = sorted(data["Category"].dropna().unique())
    selected_regions = st.multiselect("🌍 Region", regions, default=regions)
    selected_categories = st.multiselect("🛍️ Category", categories, default=categories)
    st.caption("Filters update every chart and KPI.")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = data[
    data["Order Date"].dt.date.between(start_date, end_date)
    & data["Region"].isin(selected_regions)
    & data["Category"].isin(selected_categories)
].copy()

if filtered.empty:
    st.warning("No rows match these filters. Change the selections in the sidebar.")
    st.stop()

sales = filtered["Sales"].sum()
profit = filtered["Profit"].sum()
orders = filtered["Order ID"].nunique() if "Order ID" in filtered.columns else len(filtered)
quantity = filtered["Quantity"].sum()
margin = (profit / sales * 100) if sales else 0
avg_order = sales / orders if orders else 0

def money(x):
    return f"${x:,.0f}"

kpis = [
    ("💰 Total Sales", money(sales), f"{len(filtered):,} order lines", "#dbeafe"),
    ("📈 Total Profit", money(profit), f"{margin:.1f}% profit margin", "#dcfce7"),
    ("🧾 Orders", f"{orders:,}", f"{quantity:,.0f} units sold", "#fef3c7"),
    ("🛒 Avg. Order Value", money(avg_order), "Sales ÷ unique orders", "#fce7f3"),
]
cols = st.columns(4)
for col, (label, value, hint, bg) in zip(cols, kpis):
    col.markdown(f'<div class="kpi" style="background:{bg}"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">✨ Business performance at a glance</div>', unsafe_allow_html=True)
left, right = st.columns([1.55, 1])
monthly = filtered.set_index("Order Date").resample("MS").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
fig = go.Figure()
fig.add_trace(go.Scatter(x=monthly["Order Date"], y=monthly["Sales"], name="Sales", mode="lines+markers", line=dict(color="#6366f1", width=4), fill="tozeroy", fillcolor="rgba(99,102,241,.12)"))
fig.add_trace(go.Scatter(x=monthly["Order Date"], y=monthly["Profit"], name="Profit", mode="lines+markers", line=dict(color="#ec4899", width=3)))
fig.update_layout(title="Monthly sales & profit trend", template="plotly_white", height=340, margin=dict(l=15,r=15,t=55,b=15), legend=dict(orientation="h",y=1.12), hovermode="x unified")
left.plotly_chart(fig, use_container_width=True)

cat = filtered.groupby("Category", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
fig_cat = px.pie(cat, names="Category", values="Sales", hole=.58, color="Category", color_discrete_sequence=["#6366f1","#06b6d4","#f472b6"], title="Sales mix by category")
fig_cat.update_layout(height=340, margin=dict(l=10,r=10,t=55,b=10), legend_title="")
right.plotly_chart(fig_cat, use_container_width=True)

c1, c2 = st.columns(2)
region = filtered.groupby("Region", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum")).sort_values("Sales", ascending=True)
fig_region = px.bar(region, x="Sales", y="Region", orientation="h", color="Profit", color_continuous_scale=["#f97316","#facc15","#22c55e"], title="Regional sales performance", text_auto=".2s")
fig_region.update_layout(template="plotly_white", height=330, margin=dict(l=10,r=10,t=55,b=15), coloraxis_colorbar_title="Profit")
c1.plotly_chart(fig_region, use_container_width=True)

products = filtered.groupby("Sub-Category", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum")).sort_values("Sales", ascending=False).head(10)
fig_prod = px.bar(products.sort_values("Profit"), x="Profit", y="Sub-Category", orientation="h", color="Sales", color_continuous_scale="Purples", title="Top sub-categories by profit")
fig_prod.update_layout(template="plotly_white", height=330, margin=dict(l=10,r=10,t=55,b=15))
c2.plotly_chart(fig_prod, use_container_width=True)

st.markdown('<div class="section-title">🔎 Product & order details</div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🏆 Top products", "📦 Category breakdown", "📋 Raw data"])
with tab1:
    product_col = "Product Name" if "Product Name" in filtered.columns else "Sub-Category"
    top = filtered.groupby(product_col, as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum")).sort_values("Sales", ascending=False).head(15)
    st.dataframe(top.style.format({"Sales":"${:,.2f}","Profit":"${:,.2f}","Quantity":"{:,.0f}"}), use_container_width=True, hide_index=True)
with tab2:
    breakdown = filtered.groupby(["Category","Sub-Category"], as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum"))
    st.dataframe(breakdown.style.format({"Sales":"${:,.2f}","Profit":"${:,.2f}","Quantity":"{:,.0f}"}), use_container_width=True, hide_index=True)
with tab3:
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download filtered data", filtered.to_csv(index=False).encode("utf-8"), "filtered_superstore_sales.csv", "text/csv")

st.caption("Demo dataset is synthetic and created for portfolio practice. Replace it with a licensed/public dataset for real business conclusions.")
