import sqlite3
import os

def clear_all_data():
    """Option 1: Clear ALL data completely"""
    print("🗑️ CLEARING ALL DATA...")
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
        
        # Delete all data
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM users")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence")
        
        conn.commit()
        conn.close()
        
        print("✅ SUCCESS: All data cleared!")
        print("🎯 Database is now completely empty.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_and_create_sample():
    """Option 2: Clear and create one sample user"""
    print("🔄 CLEAR AND CREATE SINGLE USER...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # Delete all existing data
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM sqlite_sequence")
        
        # Create one fresh user
        cursor.execute('''
            INSERT INTO users (email, password, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', ('user@example.com', 'password123', 'John', 'Doe'))
        
        user_id = cursor.lastrowid
        
        # Add a few sample transactions
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
        
    except Exception as e:
        print(f"❌ Error: {e}")

def nuclear_option():
    """Option 3: Delete entire database file"""
    print("💥 NUCLEAR OPTION - DELETE DATABASE FILE...")
    print("=" * 50)
    
    if os.path.exists('finance.db'):
        os.remove('finance.db')
        print("✅ Database file 'finance.db' deleted!")
        print("🎯 When you restart the app, a new empty database will be created.")
    else:
        print("❌ Database file 'finance.db' not found.")

def show_menu():
    print("\n🎯 FINANCE DATA CLEANER")
    print("=" * 40)
    print("1. Clear ALL data (keep empty database)")
    print("2. Clear and create ONE sample user")
    print("3. Nuclear option (delete database file)")
    print("4. Exit")
    print("=" * 40)

# Main program
if __name__ == "__main__":
    show_menu()
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                clear_all_data()
                break
            elif choice == "2":
                clear_and_create_sample()
                break
            elif choice == "3":
                nuclear_option()
                break
            elif choice == "4":
                print("👋 Exit without changes.")
                break
            else:
                print("❌ Invalid choice! Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print("\n💡 Tip: Restart your app with 'python app.py' to see changes.")