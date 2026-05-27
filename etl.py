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


def get_status_general(order):   #defines order general status as there is no info in file
    if order.get("cancelled_at"):
        return "cancelled"
    elif order.get("closed_at"):
        return "closed"
    else:
        return "open"

#Mapping Shopify orders into DB:

def map_shopify_orders (orders):
    result = []
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
            "currency":           order.get("currency", "UAH"),
            "line_items":         order.get("line_items", [])
        })
    return result


#Mapping Shopify products into DB:

def map_shopify_products(products):
    result = []
    for product in products:
        result.append({
            "id":           generate_id(),
            "original_id":  str(product["id"]),
            "source":       "Shopify",
            "title":        product.get("title", ""),
            "product_type": product.get("product_type", ""),
            "status":       product.get("status", ""),
            "created_at":   product.get("created_at", "")[:10]
        })
    return result


 #Mapping Shopify order line items to unified schema
def map_shopify_order_details(orders):
    result = []
    for order in orders:
        for item in order.get("line_items", []):
            result.append({
                "id":          generate_id(),
                "order_id":    str(order["id"]),
                "product_id":  str(item.get("variant_id", "")),
                "title":       item.get("title", ""),
                "quantity":    item.get("quantity", 0),
                "total_price": round(float(item.get("price", 0)) * item.get("quantity", 0), 2)
            })
    return result

#Maps Shopify transactions to unified schema:

def map_shopify_transactions(transactions):
    result = []
    for transaction in transactions:
        result.append({
            "id":             generate_id(),
            "original_id":    str(transaction.get("id", "")),
            "order_id":       str(transaction.get("source_order_id", "")),
            "tx_type":        transaction.get("type", ""),
            "cost":           float(transaction.get("net") or 0),
            "currency":       transaction.get("currency", ""),
            "transaction_ts": transaction.get("processed_at", "")[:10],
            "status":         transaction.get("payout_status", "")
        })
    return result

