"""
app.py
-------
AI-Powered Sales Insights Assistant

A Streamlit dashboard where a user can either browse standard sales
visuals OR type a plain-English question ("Which region underperformed
and why?") and get an AI-generated answer grounded in the real
aggregated numbers from the dataset (not hallucinated).

Run locally:
    streamlit run app.py

Needs an Anthropic API key set as an environment variable:
    export ANTHROPIC_API_KEY="your-key-here"      (Mac/Linux)
    setx ANTHROPIC_API_KEY "your-key-here"         (Windows)
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px
from anthropic import Anthropic

st.set_page_config(page_title="Sales Insights Assistant", layout="wide")

# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/sales_clean.csv", parse_dates=["Order_Date"])
    return df

df = load_data()

# ---------------------------------------------------------------------
# Pre-compute summary tables (this is what grounds the AI's answers --
# it only ever reasons over real numbers, never the raw 6000 rows)
# ---------------------------------------------------------------------
def build_context(df: pd.DataFrame) -> str:
    by_region = df.groupby("Region").agg(
        Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum")
    ).round(0)
    by_region["Profit_Margin_%"] = (by_region["Total_Profit"] / by_region["Total_Sales"] * 100).round(1)

    by_category = df.groupby("Category").agg(
        Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum")
    ).round(0)
    by_category["Profit_Margin_%"] = (by_category["Total_Profit"] / by_category["Total_Sales"] * 100).round(1)

    by_month = df.groupby(df["Order_Date"].dt.to_period("M").astype(str)).agg(
        Total_Sales=("Sales", "sum")
    ).round(0)

    by_segment = df.groupby("Segment").agg(
        Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum")
    ).round(0)

    context = f"""
SALES DATA SUMMARY (aggregated from {len(df)} orders, {df['Order_Date'].min().date()} to {df['Order_Date'].max().date()})

By Region:
{by_region.to_string()}

By Category:
{by_category.to_string()}

By Segment:
{by_segment.to_string()}

Monthly Sales (most recent 6 months):
{by_month.tail(6).to_string()}
"""
    return context

context_str = build_context(df)

# ---------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))

filtered = df[df["Region"].isin(regions) & df["Category"].isin(categories)]

# ---------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------
st.title("📊 AI-Powered Sales Insights Assistant")
st.caption("Ask questions in plain English, or browse the dashboard below.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${filtered['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"${filtered['Profit'].sum():,.0f}")
avg_margin = (filtered["Profit"].sum() / filtered["Sales"].sum() * 100) if filtered["Sales"].sum() else 0
col3.metric("Avg Profit Margin", f"{avg_margin:.1f}%")
col4.metric("Orders", f"{len(filtered):,}")

# ---------------------------------------------------------------------
# AI Query box
# ---------------------------------------------------------------------
st.subheader("💬 Ask the data a question")
question = st.text_input(
    "e.g. Which region underperformed last quarter and why?",
    key="question",
)

if st.button("Ask") and question:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("No ANTHROPIC_API_KEY found. Set it as an environment variable before running the app.")
    else:
        with st.spinner("Analyzing..."):
            client = Anthropic(api_key=api_key)
            prompt = f"""You are a data analyst assistant. Answer the user's question using
ONLY the sales summary data below. Be specific, cite numbers from the data,
and keep the answer to 3-5 sentences unless more detail is clearly needed.

{context_str}

Question: {question}
"""
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            answer = response.content[0].text
            st.success(answer)

st.divider()

# ---------------------------------------------------------------------
# Dashboard visuals
# ---------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Sales by Region")
    region_summary = filtered.groupby("Region")["Sales"].sum().reset_index()
    fig = px.bar(region_summary, x="Region", y="Sales", color="Region")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Profit Margin by Category")
    cat_summary = filtered.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    cat_summary["Margin_%"] = (cat_summary["Profit"] / cat_summary["Sales"] * 100).round(1)
    fig2 = px.bar(cat_summary, x="Category", y="Margin_%", color="Category")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Monthly Sales Trend")
monthly = filtered.groupby(filtered["Order_Date"].dt.to_period("M").astype(str))["Sales"].sum().reset_index()
monthly.columns = ["Month", "Sales"]
fig3 = px.line(monthly, x="Month", y="Sales", markers=True)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Raw Data (filtered)")
st.dataframe(filtered.sort_values("Order_Date", ascending=False), use_container_width=True)
