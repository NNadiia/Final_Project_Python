# E-Commerce Analytics Project
### ReDI School Munich — Python Course Final Project 2026

## Project Description
This project integrates data from two e-commerce platforms (Shopify and eBay),
maps them into a unified SQLite database, calculates key business metrics (KPIs)
using SQL queries, and visualizes the results with interactive Plotly charts.

## Project Structure
Final_Project_Python/
  main.py              - runs the full pipeline
  etl.py               - Extract, Transform, Load
  db.py                - database structure and validation
  analytics.py         - SQL queries and KPIs
  charts.py            - Plotly visualizations
  test_db_py.py        - unit tests
  requirements.txt     - project dependencies
  Shopify_05_26.txt    - Shopify data (JSON)
  Ebay_26_05_26.txt    - eBay data (JSON)
  Mapping.xlsx         - data mapping documentation

## Database Schema
Table - Description
EcomOrders - All orders from both platforms
EcomOrderDetails - Order line items
EcomProducts - Products from both platforms
EcomTransactions - Payment transactions

## KPIs
- Total revenue by source (Shopify vs eBay)
- Orders count and revenue by month
- Top-5 products by revenue
- Orders by financial status

## Dashboard
Interactive dashboard built with Plotly - opens in browser.
Click on legend to filter by source.

## Future Improvements
- Add date range filter
- Add category filter
- Currency normalization to USD
- Store historical data with loaded_at timestamp
- Add total summary chart to dashboard
- Interactive dashboard using Plotly Dash

## How to Run
1. Clone the repository:
git clone https://github.com/NNadiia/Final_Project_Python.git
cd Final_Project_Python

2. Create and activate virtual environment:
python -m venv ecommerce_venv
ecommerce_venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt

4. Run the project:
python main.py

## Technologies
- Python 3.14
- SQLite3 (built-in)
- Plotly
- Pandas
- json (built-in)
- uuid (built-in)
- pathlib (built-in)

## Author
Nadiia — ReDI School Munich, Python Course 2026