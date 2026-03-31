import mysql.connector
from mysql.connector import Error
import tkinter.messagebox as messagebox

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '27july',
    'database': 'atm'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
        return None

def init_database():
    """Initialize database tables if they don't exist"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100),
                    father_name VARCHAR(100),
                    email VARCHAR(100),
                    address VARCHAR(200),
                    city VARCHAR(50),
                    province VARCHAR(50),
                    pin_code VARCHAR(10),
                    cnic VARCHAR(20),
                    card_number VARCHAR(20) UNIQUE,
                    pin VARCHAR(10),
                    balance DECIMAL(10,2) DEFAULT 0
                )
            """)
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    card_number VARCHAR(20),
                    type VARCHAR(20),
                    amount DECIMAL(10,2),
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            print("Database initialized successfully")
        except Error as e:
            print(f"Error initializing database: {e}")