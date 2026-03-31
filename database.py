import mysql.connector
from mysql.connector import Error
import random
from db_config import get_db_connection

def generate_card_details():
    """Generate random card number and PIN"""
    card_no = "".join([str(random.randint(0, 9)) for _ in range(16)])
    formatted_card = " ".join([card_no[i:i+4] for i in range(0, 16, 4)])
    pin = "".join([str(random.randint(0, 9)) for _ in range(4)])
    return formatted_card, pin

def create_user(user_data):
    """Insert a new user into the database"""
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Generate unique card number and PIN
        while True:
            card_number, pin = generate_card_details()
            # Remove spaces for storage
            card_number_db = card_number.replace(" ", "")
            
            # Check if card number already exists
            cursor.execute("SELECT id FROM users WHERE card_number = %s", (card_number_db,))
            if not cursor.fetchone():
                break
        
        # Insert user data
        query = """
            INSERT INTO users (
                full_name, father_name, email, address, city, province, 
                pin_code, cnic, card_number, pin, balance
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            user_data['full_name'],
            user_data['father_name'],
            user_data['email'],
            user_data['address'],
            user_data['city'],
            user_data['province'],
            user_data['pin_code'],
            user_data['cnic'],
            card_number_db,
            pin,
            0.00  # Initial balance
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, (card_number, pin)
        
    except Error as e:
        return False, f"Database error: {e}"

def verify_login(card_number, pin):
    """Verify user login credentials"""
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Remove spaces if user entered formatted card number
        card_number_db = card_number.replace(" ", "")
        
        query = "SELECT * FROM users WHERE card_number = %s AND pin = %s"
        cursor.execute(query, (card_number_db, pin))
        
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user:
            return True, user
        else:
            return False, "Invalid card number or PIN"
            
    except Error as e:
        return False, f"Database error: {e}"

def get_user_by_card(card_number):
    """Get user details by card number"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Remove spaces if user entered formatted card number
        card_number_db = card_number.replace(" ", "")
        
        query = "SELECT * FROM users WHERE card_number = %s"
        cursor.execute(query, (card_number_db,))
        
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return user
        
    except Error as e:
        print(f"Error: {e}")
        return None

def update_balance(card_number, new_balance):
    """Update user balance"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "UPDATE users SET balance = %s WHERE card_number = %s"
        cursor.execute(query, (new_balance, card_number))
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error: {e}")
        return False

def add_transaction(card_number, trans_type, amount):
    """Add a transaction record"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "INSERT INTO transactions (card_number, type, amount) VALUES (%s, %s, %s)"
        cursor.execute(query, (card_number, trans_type, amount))
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error: {e}")
        return False

def get_transactions(card_number, limit=10):
    """Get recent transactions for a user"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT * FROM transactions 
            WHERE card_number = %s 
            ORDER BY date DESC 
            LIMIT %s
        """
        cursor.execute(query, (card_number, limit))
        
        transactions = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return transactions
        
    except Error as e:
        print(f"Error: {e}")
        return []

def update_pin(card_number, new_pin):
    """Update user PIN"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "UPDATE users SET pin = %s WHERE card_number = %s"
        cursor.execute(query, (new_pin, card_number))
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error: {e}")
        return False