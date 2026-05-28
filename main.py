from etl import run_etl

if __name__ == "__main__":   #runs the full data integration process with json data files
    run_etl( shopify_file="Shopify_05_26.txt", ebay_file="Ebay_26_05_26.txt")