import sqlite3
import uuid

DB_NAME = "ecommerce.db"

#generating unique ID as we have several data sources
def generate_id():
    return str(uuid.uuid4())


# create tables in DB for data mapping
def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        
        cursor.execute ("""
                CREATE TABLE IF NOT EXISTS EcomOrders (         
                    id TEXT PRIMARY KEY,
                    original_id TEXT,
                    source TEXT,
                    create_date TEXT,
                    amount REAL,
                    cost  REAL,
                    cost_with_discount REAL,
                    total_quantity INTEGER,
                    status_general TEXT,
                    status_financial TEXT,
                    currency TEXT
             )
         """)                                                       


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS EcomProducts (
                id          TEXT PRIMARY KEY,
                original_id TEXT,
                source      TEXT,
                title       TEXT,
                product_type TEXT,
                status      TEXT,
                created_at  TEXT
            )
        """)

        cursor.execute ("""
                CREATE TABLE IF NOT EXISTS EcomOrderDetails (
                    id  TEXT PRIMARY KEY, 
                    order_id TEXT, 
                    product_id TEXT,     
                    title TEXT,
                    quantity INTEGER,
                    total_price REAL,
                    FOREIGN KEY (order_id) REFERENCES EcomOrders(id),
                    FOREIGN KEY (product_id) REFERENCES EcomProducts(id)
             )
         """)

        cursor.execute ("""
                CREATE TABLE IF NOT EXISTS EcomTransactions (
                    id TEXT PRIMARY KEY,
                    original_id TEXT,
                    order_id TEXT,
                    tx_type TEXT,
                    cost REAL,
                    currency TEXT,
                    transaction_ts TEXT,
                    status TEXT,
                    FOREIGN KEY (order_id) REFERENCES EcomOrders(id)
            )
        """)

 #Clears all tables before new load
 #Future improvement: store historical data with loaded_at timestamp instead of clearing

def clear_tables():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        for table in ["EcomTransactions", "EcomOrderDetails", 
                      "EcomProducts", "EcomOrders"]:
            cursor.execute(f"DELETE FROM {table}")