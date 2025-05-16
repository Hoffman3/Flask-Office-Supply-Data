import os
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

data_path = os.path.join(os.path.dirname(__file__), 'data', 'TableauSalesData.csv')

# check if the dataset exists
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Dataset not found: {data_path}")

try:
    df = pd.read_csv(data_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%y', errors='coerce')
    df['Year'] = df['Order Date'].dt.year  # Extract year for analysis
except Exception as e:
    raise ValueError(f"Error reading dataset: {str(e)}")


@app.route("/", methods=["GET", "POST"])
def index():
    """Handles the main page rendering and query processing."""

    query_result = None 

  
    categories = sorted(df['Category'].dropna().unique())  # Sorted for better UX
    sub_categories = sorted(df['Sub-Category'].dropna().unique())
    regions = sorted(df['Region'].dropna().unique())
    segments = sorted(df['Segment'].dropna().unique())

    if request.method == "POST":
    
        category = request.form.get("category")
        sub_category = request.form.get("sub_category")
        region = request.form.get("region")
        segment = request.form.get("segment")
        query = request.form.get("query")

        category = category if category in categories else None
        sub_category = sub_category if sub_category in sub_categories else None
        region = region if region in regions else None
        segment = segment if segment in segments else None

        filtered_df = df.copy()
        filters = {
            'Category': category,
            'Sub-Category': sub_category,
            'Region': region,
            'Segment': segment
        }

        for column, value in filters.items():
            if value:
                filtered_df = filtered_df[filtered_df[column] == value]

        # query selection
        if query == "Total Sales and Profit":
            total_sales = filtered_df['Sales'].sum()
            total_profit = filtered_df['Profit'].sum()
            query_result = f"Total Sales: ${total_sales:,.2f}, Total Profit: ${total_profit:,.2f}"

        elif query == "Average Discount by Product":
            avg_discount = filtered_df.groupby('Product Name')['Discount'].mean().sort_values(ascending=False)
            query_result = avg_discount.to_frame('Average Discount').reset_index().to_html(index=False)

        elif query == "Total Sales by Year":
            sales_by_year = filtered_df.groupby('Year')['Sales'].sum()
            query_result = sales_by_year.to_frame('Total Sales').reset_index().to_html(index=False)

        elif query == "Profit by Region":
            profit_by_region = filtered_df.groupby('Region')['Profit'].sum()
            query_result = profit_by_region.to_frame('Total Profit').reset_index().to_html(index=False)

        elif query == "Products with Negative Profit":
            negative_profit = filtered_df[filtered_df['Profit'] < 0][['Product Name', 'Profit']]
            query_result = negative_profit.to_html(index=False)

    return render_template(
        "index.html",
        categories=categories,
        sub_categories=sub_categories,
        regions=regions,
        segments=segments,
        query_result=query_result,
    )


if __name__ == "__main__":
    app.run(debug=True)
