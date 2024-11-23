import os
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Path to the CSV file relative to the project directory
data_path = os.path.join(os.path.dirname(__file__), 'data', 'TableauSalesData.csv')

# Check if the file exists before proceeding
if not os.path.exists(data_path):
    raise FileNotFoundError(f"The file was not found: {data_path}")

# Load the dataset
try:
    df = pd.read_csv(data_path)
    # Parse the 'Order Date' column with the correct format
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%y', errors='coerce')
    df['Year'] = df['Order Date'].dt.year
except Exception as e:
    raise ValueError(f"An error occurred while reading the data: {str(e)}")

@app.route("/", methods=["GET", "POST"])
def index():
    query_result = None

    # Dropdown options
    categories = df['Category'].dropna().unique()
    sub_categories = df['Sub-Category'].dropna().unique()
    regions = df['Region'].dropna().unique()
    segments = df['Segment'].dropna().unique()

    if request.method == "POST":
        # Retrieve form inputs
        category = request.form.get("category")
        sub_category = request.form.get("sub_category")
        region = request.form.get("region")
        segment = request.form.get("segment")
        query = request.form.get("query")

        # Sanitize inputs
        category = category if category in categories else None
        sub_category = sub_category if sub_category in sub_categories else None
        region = region if region in regions else None
        segment = segment if segment in segments else None

        # Filter data based on inputs
        filtered_df = df.copy()
        if category:
            filtered_df = filtered_df[filtered_df['Category'] == category]
        if sub_category:
            filtered_df = filtered_df[filtered_df['Sub-Category'] == sub_category]
        if region:
            filtered_df = filtered_df[filtered_df['Region'] == region]
        if segment:
            filtered_df = filtered_df[filtered_df['Segment'] == segment]

        # Perform the selected query
        if query == "Total Sales and Profit":
            total_sales = filtered_df['Sales'].sum()
            total_profit = filtered_df['Profit'].sum()
            query_result = f"Total Sales: ${total_sales:.2f}, Total Profit: ${total_profit:.2f}"
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
            negative_profit = filtered_df[filtered_df['Profit'] < 0]
            query_result = negative_profit[['Product Name', 'Profit']].to_html(index=False)

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

