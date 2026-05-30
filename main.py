from etl import run_etl
from analytics import get_revenue_by_source, get_orders_by_month, get_top_products, get_total_summary, get_orders_by_status
from charts import     plot_dashboard
#from charts import plot_revenue_by_source, plot_orders_by_month, plot_top_products, plot_orders_by_status


if __name__ == "__main__":   #runs the full data integration process with json data files
    run_etl( shopify_file="Shopify_05_26.txt", ebay_file="Ebay_26_05_26.txt")

    get_revenue_by_source()
    get_orders_by_month()
    get_top_products()
    get_orders_by_status()
    get_total_summary()

    plot_dashboard()
