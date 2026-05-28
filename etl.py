"""
etl.py — Extract, Transform, Load
Reads data from Shopify and eBay JSON files, maps them into a unified schema and saves to SQLite.
"""

import json
import sqlite3
from db import generate_id, create_tables, clear_tables, DB_NAME, check_status


def load_json (filename):   #reads JSON file and returns data
    with open (filename, "r", encoding = "utf-8") as file:
        data = json.load(file)
        print (f"Loaded {filename}")
    return data


ORDER_STATUSES = [
    "open", "closed", "cancelled", "pending", "authorized", "partially_paid", "paid", "partially_refunded", "refunded", "voided"
]

TX_TYPES = [
    "SALE", "REFUND", "CREDIT", "DISPUTE", "CHARGE", "RESERVE", "ADJUSTMENT", "DEBIT", "PAYOUT", "PAYOUT_FAILURE", "PAYOUT_CANCELLATION"
]

def check_status(status):
    if status in ORDER_STATUSES:
        return status
    return None


def check_tx_type(tx_type): 
    if tx_type in TX_TYPES:
        return tx_type
    return None


def get_status_general(order):   #defines general order status as there is no info in file
    if order.get("cancelled_at"):
        return "cancelled"
    elif order.get("closed_at"):
        return "closed"
    else:
        return "open"

#Mapping Shopify orders into DB:

def map_shopify_orders (orders):
    result = []
    if not orders:
        return result
    
    for order in orders:
                
        total_qty = 0
        for item in order.get("line_items", []):
            total_qty += item.get("quantity", 0)

        result.append({
                "id": generate_id(),
                "original_id": str(order["id"]),
                "source": "Shopify",
                "create_date": order["created_at"][:10],
                "amount": float(order.get("subtotal_price") or 0),
                "cost": float(order.get("subtotal_price") or 0) + float(order.get("total_tax") or 0),
                "cost_with_discount": float(order.get("total_price") or 0),
                "total_quantity": total_qty,
                "status_general": get_status_general(order),
                "status_financial":check_status(order.get("financial_status", "")),
                "currency": "USD",  # order.get("currency", "UAH") -future improvement: currency normalization to USD
                "line_items": order.get("line_items", []) 
        })
    return result


#Mapping Shopify products into DB:

def map_shopify_products(products):
    result = []
    if not products:
        return result

    for product in products:
        result.append({
            "id": generate_id(),
            "original_id": str(product["id"]),
            "source": "Shopify",
            "title": product.get("title", ""),
            "product_type": product.get("product_type", ""),
            "status":  product.get("status", ""),
            "created_at": product.get("created_at", "")[:10]
        })
    return result


 #Mapping Shopify order line items into DB
def map_shopify_order_details(orders):
    result = []
    if not orders:
        return result
    
    for order in orders:
        for item in order.get("line_items", []):
            result.append({
                "id":  generate_id(),
                "order_id": str(order["id"]),
                "product_id": str(item.get("variant_id", "")),
                "title": item.get("title", ""),
                "quantity": item.get("quantity", 0),
                "total_price": round(float(item.get("price", 0)) * item.get("quantity", 0), 2)
            })
    return result


#Maps Shopify transactions into DB:
def map_shopify_transactions(transactions):
    result = []
    if not transactions:
        return result
    
    for transaction in transactions:
        result.append({
            "id": generate_id(),
            "original_id": str(transaction.get("id", "")),
            "order_id": str(transaction.get("source_order_id", "")),
            "tx_type": check_tx_type(transaction.get("type", "").upper()),
            "cost":  float(transaction.get("net") or 0),
            "currency": transaction.get("currency", "USD"),
            "transaction_ts": transaction.get("processed_at", "")[:10],
            "status": transaction.get("payout_status", "")
        })
    return result


#Mapping eBay orders into DB
def map_ebay_orders(orders):
    result = []
    if not orders:
        return result
    
    for order in orders:
        price = order.get("pricingSummary", {})
        subtotal = float(price.get("priceSubtotal", {}).get("value", 0))
        delivery = float(price.get("deliveryCost", {}).get("value", 0))
        total    = float(price.get("total", {}).get("value", 0))

        total_qty = 0
        for item in order.get("lineItems", []):
            total_qty += item.get("quantity", 0)


        fulfillment = order.get("orderFulfillmentStatus", "")  #Defines general order status based on orderFulfillmentStatus from eBay
        if fulfillment == "FULFILLED":
            status_general = "closed"
        elif fulfillment == "NOT_STARTED":
            status_general = "open"
        else:
            status_general = "open"


        result.append({
            "id": generate_id(),
            "original_id": order.get("orderId", ""),
            "source": "eBay",
            "create_date": order.get("creationDate", "")[:10],
            "amount": subtotal,
            "cost": subtotal + delivery,
            "cost_with_discount": total,
            "total_quantity": total_qty,
            "status_general": check_status(status_general),
            "status_financial": check_status(order.get("orderPaymentStatus", "").lower()),
            "currency": price.get("total", {}).get("currency", "USD"),
            "line_items": order.get("lineItems", [])
        })
    return result


#Mapping eBay products into DB
def map_ebay_products(products):
    result = []
    if not products:
       return result
    
    unique_product_ids = set()
    items = products["GetAdvancedItem"]["findItemsAdvancedResponse"]["searchResult"]["item"]
    for item in items:
        original_id = str(item.get("itemId", ""))
        if original_id not in unique_product_ids:
            unique_product_ids.add(original_id)
            result.append({
                "id":  generate_id(),
                "original_id": str(item.get("itemId", "")),
                "source":  "eBay",
                "title": item.get("title", ""),
                "product_type": item.get("primaryCategory", {}).get("categoryName", ""),
                "status": item.get("condition", {}).get("conditionDisplayName", ""),
                "created_at": item.get("listingInfo", {}).get("startTime", "")[:10]
            })
    return result

#Mapping eBay order line items into DB
def map_ebay_order_details(orders):
    result = []
    if not orders:
        return result
    
    for order in orders:
        for item in order.get("lineItems", []):
            result.append({
                "id": generate_id(),
                "order_id": order.get("orderId", ""),
                "product_id": str(item.get("lineItemId", "")),
                "title":  item.get("title", ""),
                "quantity": item.get("quantity", 0),
                "total_price": float(item.get("total", {}).get("value", 0))
            })
    return result

#Mapping eBay transactions into DB
def map_ebay_transactions(data):
    result = []
    txns = data.get("GetOrderTransactions", [])
    if not txns:
        return result
    
    response = txns[0].get("GetOrderTransactionsResponse", {})
    order = response.get("OrderArray", {}).get("Order", {})
    if not order:
        return result

    status = order.get("CheckoutStatus", {}).get("Status", "")
    if status == "Complete":
        tx_type = "SALE"
    elif status == "Failed":
        tx_type = "REFUND"
    else:
        tx_type = "SALE"

    if order:
        result.append({
            "id":  generate_id(),
            "original_id":order.get("ExtendedOrderID", ""),
            "order_id": order.get("OrderID", ""),
            "tx_type":  check_tx_type(tx_type),
            "cost":  float(order.get("AmountPaid", {}).get("#text", 0)),
            "currency": order.get("AmountPaid", {}).get("@currencyID", "USD"),
            "transaction_ts": order.get("PaidTime", "")[:10],
            "status": status
        })
    return result


# --- Save functions ---

#Saves orders to EcomOrders table
def save_orders(orders):
    data = []
    for order in orders:
        data.append((
            order["id"],
            order["original_id"],
            order["source"],
            order["create_date"],
            order["amount"],
            order["cost"],
            order["cost_with_discount"],
            order["total_quantity"],
            order["status_general"],
            order["status_financial"],
            order["currency"]
        ))
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO EcomOrders (id, original_id, source, create_date,amount, cost, cost_with_discount, total_quantity,"
                "status_general, status_financial, currency) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    except sqlite3.Error as e:
        print("Database error", e)


#Saves products to EcomProducts table
def save_products(products):
    data = []
    for product in products:
        data.append((
            product["id"],
            product["original_id"],
            product["source"],
            product["title"],
            product["product_type"],
            product["status"],
            product["created_at"]
        ))
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO EcomProducts (id, original_id, source, title, product_type, status, created_at)"
                 "VALUES (?, ?, ?, ?, ?, ?, ?)", data
            )
    except sqlite3.Error as e:
        print("Database error:", e)


#Saves order details to EcomOrderDetails table
def save_order_details(order_details):
    data = []
    for detail in order_details:
        data.append((
            detail["id"],
            detail["order_id"],
            detail["product_id"],
            detail["title"],
            detail["quantity"],
            detail["total_price"]
        ))
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO EcomOrderDetails (id, order_id, product_id, title, quantity, total_price)"
                "VALUES (?, ?, ?, ?, ?, ?)", data
            )
    except sqlite3.Error as e:
        print("Database error:", e)     


#Saves transactions to EcomTransactions table
def save_transactions(transactions):
    data = []
    for transaction in transactions:
        data.append((
            transaction["id"],
            transaction["original_id"],
            transaction["order_id"],
            transaction["tx_type"],
            transaction["cost"],
            transaction["currency"],
            transaction["transaction_ts"],
            transaction["status"]
        ))
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO EcomTransactions (id, original_id, order_id, tx_type, cost, currency, transaction_ts, status)"
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data
            )
    except sqlite3.Error as e:
        print("Database error:", e)           


# --- Main ETL function ---
def run_etl(shopify_file, ebay_file):
    print("Starting ETL")

    # Extract
    shopify_data = load_json(shopify_file)
    ebay_data    = load_json(ebay_file)

    # Transform
    shopify_orders   = map_shopify_orders(shopify_data.get("GetOrders", []))
    shopify_products = map_shopify_products(shopify_data.get("GetProducts", []))
    shopify_details  = map_shopify_order_details(shopify_data.get("GetOrders", []))
    shopify_txns     = map_shopify_transactions(shopify_data.get("GetTransactions", []))

    ebay_orders   = map_ebay_orders(ebay_data.get("GetOrders", []))
    ebay_products = map_ebay_products(ebay_data)
    ebay_details  = map_ebay_order_details(ebay_data.get("GetOrders", []))
    ebay_txns     = map_ebay_transactions(ebay_data)

    # Load
    create_tables()
    clear_tables()

    save_orders(shopify_orders + ebay_orders)
    save_products(shopify_products + ebay_products)
    save_order_details(shopify_details + ebay_details)
    save_transactions(shopify_txns + ebay_txns)

    print("ETL completed!")        