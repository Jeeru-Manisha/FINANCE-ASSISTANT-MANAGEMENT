import sqlite3
import os

def reset_database():
    print("🔄 RESETTING FINANCE DATABASE")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Count current data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transactions")
        transaction_count = cursor.fetchone()[0]
        
        print(f"📊 Current Data:")
        print(f"   👥 Users: {user_count}")
        print(f"   💳 Transactions: {transaction_count}")
        
        # Ask for confirmation
        response = input("\n❓ Are you sure you want to delete ALL data? (yes/no): ").lower().strip()
        
        if response in ['yes', 'y']:
            # Delete all data but keep table structure
            cursor.execute("DELETE FROM transactions")
            cursor.execute("DELETE FROM users")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'transactions')")
            
            conn.commit()
            conn.close()
            
            print("✅ SUCCESS: All data cleared!")
            print("🎯 Database is now empty and ready for one fresh user.")
            
        else:
            print("❌ Reset cancelled. No data was deleted.")
            conn.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")

def reset_and_create_sample():
    """Reset everything and create one sample user"""
    print("🔄 RESET AND CREATE SINGLE USER")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Delete all existing data
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'transactions')")
        
        # Create one fresh user
        cursor.execute('''
            INSERT INTO users (email, password, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', ('user@example.com', 'password123', 'John', 'Doe'))
        
        user_id = cursor.lastrowid
        
        # Add a few sample transactions for the new user
        sample_transactions = [
            (user_id, 3000, 'income', 'Salary', 'Monthly income'),
            (user_id, -800, 'expense', 'Rent', 'Apartment rent'),
            (user_id, -300, 'expense', 'Food', 'Groceries'),
        ]
        
        cursor.executemany('''
            INSERT INTO transactions (user_id, amount, type, category, description)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_transactions)
        
        conn.commit()
        conn.close()
        
        print("✅ SUCCESS: Database reset complete!")
        print(f"👤 New User Created:")
        print(f"   ID: {user_id}")
        print(f"   Email: user@example.com")
        print(f"   Name: John Doe")
        print(f"   📊 Added 3 sample transactions")
        print(f"\n🎯 You now have exactly ONE user with sample data!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Choose reset option:")
    print("1. Clear ALL data (empty database)")
    print("2. Clear and create one sample user")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        reset_database()
    elif choice == "2":
        reset_and_create_sample()
    else:
        print("❌ Invalid choice")