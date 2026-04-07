"""
setup_db.py — Sample Business Database Creator
Yeh script ek realistic business database banata hai demo ke liye
"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_database(db_path="business.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── Tables ──────────────────────────────────────────────
    cursor.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            id         INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            email      TEXT,
            city       TEXT,
            country    TEXT,
            join_date  TEXT
        );

        CREATE TABLE products (
            id        INTEGER PRIMARY KEY,
            name      TEXT NOT NULL,
            category  TEXT,
            price     REAL,
            stock     INTEGER
        );

        CREATE TABLE orders (
            id           INTEGER PRIMARY KEY,
            customer_id  INTEGER REFERENCES customers(id),
            product_id   INTEGER REFERENCES products(id),
            quantity     INTEGER,
            total_amount REAL,
            order_date   TEXT,
            status       TEXT
        );
    """)

    # ── Customers ────────────────────────────────────────────
    customers = [
        (1,  "Ahmed Ali",      "ahmed@email.com",   "Karachi",     "Pakistan",   "2023-01-15"),
        (2,  "Sara Khan",      "sara@email.com",    "Lahore",      "Pakistan",   "2023-02-20"),
        (3,  "John Smith",     "john@email.com",    "New York",    "USA",        "2023-03-10"),
        (4,  "Maria Garcia",   "maria@email.com",   "Madrid",      "Spain",      "2023-04-05"),
        (5,  "Wei Chen",       "wei@email.com",     "Shanghai",    "China",      "2023-05-12"),
        (6,  "Fatima Hassan",  "fatima@email.com",  "Dubai",       "UAE",        "2023-06-18"),
        (7,  "David Brown",    "david@email.com",   "London",      "UK",         "2023-07-22"),
        (8,  "Priya Patel",    "priya@email.com",   "Mumbai",      "India",      "2023-08-30"),
        (9,  "Carlos Lopez",   "carlos@email.com",  "Mexico City", "Mexico",     "2023-09-14"),
        (10, "Emma Wilson",    "emma@email.com",    "Sydney",      "Australia",  "2023-10-01"),
        (11, "Omar Sheikh",    "omar@email.com",    "Islamabad",   "Pakistan",   "2023-11-05"),
        (12, "Sophie Dubois",  "sophie@email.com",  "Paris",       "France",     "2023-12-12"),
    ]

    # ── Products ─────────────────────────────────────────────
    products = [
        (1,  "Laptop Pro X",               "Electronics", 1299.99, 50),
        (2,  "Wireless Mouse",             "Electronics",   29.99, 200),
        (3,  "Office Chair",               "Furniture",    349.99,  30),
        (4,  "Standing Desk",              "Furniture",    599.99,  20),
        (5,  "Python Masterclass Course",  "Education",     99.99, 999),
        (6,  "AI Automation Toolkit",      "Software",     199.99, 999),
        (7,  "Noise Cancelling Headphones","Electronics",  249.99,  75),
        (8,  "Mechanical Keyboard",        "Electronics",  149.99, 100),
        (9,  "4K Monitor",                 "Electronics",  449.99,  40),
        (10, "HD Webcam",                  "Electronics",   79.99, 150),
        (11, "Power BI Dashboard Template","Software",      49.99, 999),
        (12, "Ergonomic Mouse Pad",        "Furniture",     19.99, 300),
    ]

    # ── Orders (60 rows, realistic) ──────────────────────────
    random.seed(42)
    statuses = ["completed", "completed", "completed", "shipped", "pending", "cancelled"]
    orders = []
    for i in range(1, 61):
        cid   = random.randint(1, 12)
        pid   = random.randint(1, 12)
        qty   = random.randint(1, 5)
        price = products[pid - 1][3]
        total = round(price * qty, 2)
        days_ago   = random.randint(1, 365)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        status     = random.choice(statuses)
        orders.append((i, cid, pid, qty, total, order_date, status))

    cursor.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", customers)
    cursor.executemany("INSERT INTO products  VALUES (?,?,?,?,?)",   products)
    cursor.executemany("INSERT INTO orders    VALUES (?,?,?,?,?,?,?)", orders)

    conn.commit()
    conn.close()
    print("[OK] Database 'business.db' successfully created!")
    print(f"   - {len(customers)} customers, {len(products)} products, {len(orders)} orders")

if __name__ == "__main__":
    create_database()
