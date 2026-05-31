import sqlite3
from db import DB_NAME

# SQL queries to calculate key business metrics:

#Total revenue by source
def get_revenue_by_source():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT source, ROUND(SUM(amount), 2) AS total_revenue, COUNT(*) AS total_orders "
            "FROM EcomOrders GROUP BY source ORDER BY total_revenue DESC")
        result = cursor.fetchall()
    print("Revenue by source", result)
    return result

#Orders and revenue by month and source
def get_orders_by_month():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT STRFTIME('%Y-%m', create_date) AS month, source, COUNT(*) AS total_orders, ROUND(SUM(amount), 2) AS total_revenue "
        "FROM EcomOrders GROUP BY month, source ORDER BY month")
        result = cursor.fetchall()
    print("Orders and revenue by month and source", result)
    return result
    

#Top 5 products by revenue and source
def get_top_products():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT d.title, o.source, SUM(d.quantity) AS total_qty, ROUND(SUM(d.total_price), 2) AS total_revenue " 
        "FROM EcomOrderDetails d JOIN EcomOrders o ON d.order_id = o.original_id " 
        "GROUP BY d.title, o.source " 
        "ORDER BY total_revenue DESC LIMIT 5")
        result = cursor.fetchall()
    print("Top 5 products by revenue and source", result)
    return result
    
#Orders by financial status
def get_orders_by_status():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status_financial, source, COUNT(*) AS total_orders, ROUND(SUM(amount), 2) AS total_revenue " 
        "FROM EcomOrders GROUP BY status_financial, source ORDER BY total_orders DESC")
        result = cursor.fetchall()
    print("Orders by financial status and source", result)
    return result


#Total summary by source
def get_total_summary():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT source, COUNT(*) AS total_orders, ROUND(SUM(amount), 2) AS total_revenue, " 
        "ROUND(AVG(amount), 2) AS avg_order_value, SUM(total_quantity) AS total_items FROM EcomOrders GROUP BY source")
        result = cursor.fetchall()
    print("Total summary by source", result)
    return result
    