# Superstore Sales Studio — Data Analyst Portfolio Project

A colourful, interactive sales analytics dashboard built with **Python, Pandas, Plotly and Streamlit**. It includes a synthetic Superstore-style sample dataset so you can run the project immediately.

## Dashboard features
- KPI cards: total sales, total profit, orders and average order value
- Date, region and category filters
- Monthly sales and profit trend
- Sales mix by category
- Regional sales performance
- Top profitable sub-categories and top products
- Category breakdown and raw data tabs
- CSV upload and filtered-data download

## Project structure
```text
superstore_sales_dashboard/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── superstore_sales.csv
```

## Run locally (Windows PowerShell)

1. Install Python 3.10 or newer from https://www.python.org/downloads/ and select **Add Python to PATH** during installation.
2. Extract the ZIP and open PowerShell in the extracted `superstore_sales_dashboard` folder.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
4. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.
5. Install dependencies:
   ```powershell
   py -m pip install -r requirements.txt
   ```
6. Start the dashboard:
   ```powershell
   py -m streamlit run app.py
   ```
7. Streamlit opens the dashboard in your browser, usually at http://localhost:8501.

## Dataset
`data/superstore_sales.csv` contains 1,200 synthetic order lines from 2023–2025 with order dates, shipping details, customer segments, regions, product categories, sales, quantity, discounts and profit. It is suitable for practicing filtering, aggregation, trend analysis and visualization. It is not official retail data and should not be presented as real company results.

## Suggested analysis questions
1. Which category contributes the most revenue?
2. Which region has the highest profit?
3. Which sub-categories generate low or negative profit?
4. How do sales change month by month?
5. What is the average order value?
6. Does discounting appear to reduce profitability?

## Power BI extension
You can import `data/superstore_sales.csv` into Power BI Desktop, set `Order Date` to Date and create measures:
```DAX
Total Sales = SUM(Superstore_Sales[Sales])
Total Profit = SUM(Superstore_Sales[Profit])
Total Quantity = SUM(Superstore_Sales[Quantity])
Profit Margin = DIVIDE([Total Profit], [Total Sales], 0)
Orders = DISTINCTCOUNT(Superstore_Sales[Order ID])
Average Order Value = DIVIDE([Total Sales], [Orders], 0)
```
Then add KPI cards, a monthly line chart, category donut chart, regional bar chart and slicers for date, region and category.

## GitHub
Create a repository named `superstore-sales-dashboard`, upload these files, and add a screenshot of the running dashboard to your README.
