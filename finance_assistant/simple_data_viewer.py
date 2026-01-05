import sqlite3
from datetime import datetime

def print_table(title, headers, data):
    """Print data in a nice table format"""
    print(f"\n{title}")
    print("=" * 80)
    
    if not data:
        print("No data found")
        return
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print headers
    header_line = " | ".join(header.ljust(width) for header, width in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print data
    for row in data:
        row_line = " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))
        print(row_line)

def view_database():
    print("🔍 FINANCE ASSISTANT - DATABASE VIEWER")
    print("=" * 60)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        # 1. View Users
        cursor.execute("SELECT id, email, first_name, last_name, created_at FROM users")
        users = cursor.fetchall()
        print_table("👥 REGISTERED USERS", 
                   ["ID", "Email", "First Name", "Last Name", "Created At"], 
                   users)
        
        # 2. View All Transactions
        cursor.execute('''
            SELECT id, user_id, amount, type, category, description, date 
            FROM transactions 
            ORDER BY date DESC
        ''')
        transactions = cursor.fetchall()
        print_table("💳 ALL TRANSACTIONS", 
                   ["ID", "UserID", "Amount", "Type", "Category", "Description", "Date"], 
                   transactions)
        
        # 3. Financial Summary
        print("\n📊 FINANCIAL SUMMARY")
        print("-" * 40)
        
        # Total Income
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
        total_income = cursor.fetchone()[0] or 0
        
        # Total Expenses
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
        total_expenses = abs(cursor.fetchone()[0] or 0)
        
        # Net Savings
        net_savings = total_income - total_expenses
        
        # Savings Rate
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
        
        print(f"💰 Total Income:    ${total_income:,.2f}")
        print(f"💸 Total Expenses:  ${total_expenses:,.2f}")
        print(f"🎯 Net Savings:     ${net_savings:,.2f}")
        print(f"📈 Savings Rate:    {savings_rate:.1f}%")
        
        # 4. Spending by Category
        cursor.execute('''
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions 
            WHERE type='expense' 
            GROUP BY category 
            ORDER BY total DESC
        ''')
        spending = cursor.fetchall()
        
        if spending:
            print("\n🎯 SPENDING BY CATEGORY")
            print("-" * 40)
            for category, total, count in spending:
                print(f"📁 {category:<15} ${abs(total):>8,.2f} ({count} transactions)")
        
        # 5. Recent Transactions (last 5)
        print("\n🕒 RECENT TRANSACTIONS (Last 5)")
        print("-" * 40)
        cursor.execute('''
            SELECT date, type, category, amount, description 
            FROM transactions 
            ORDER BY date DESC 
            LIMIT 5
        ''')
        recent = cursor.fetchall()
        
        for date, trans_type, category, amount, description in recent:
            sign = "+" if amount >= 0 else "-"
            color = "🟢" if amount >= 0 else "🔴"
            print(f"{color} {date[:10]} | {trans_type:<8} | {category:<12} | {sign}${abs(amount):>8,.2f} | {description}")
        
        # 6. User-specific summary
        print("\n👤 USER SUMMARY")
        print("-" * 40)
        cursor.execute("SELECT id, first_name, last_name FROM users")
        users = cursor.fetchall()
        
        for user_id, first_name, last_name in users:
            # User's transactions
            cursor.execute('''
                SELECT COUNT(*), 
                       SUM(CASE WHEN type='income' THEN amount ELSE 0 END),
                       SUM(CASE WHEN type='expense' THEN amount ELSE 0 END)
                FROM transactions 
                WHERE user_id = ?
            ''', (user_id,))
            count, income, expenses = cursor.fetchone()
            expenses = abs(expenses or 0)
            income = income or 0
            net = income - expenses
            
            print(f"User {user_id}: {first_name} {last_name}")
            print(f"   📊 Transactions: {count}")
            print(f"   💰 Total Income: ${income:,.2f}")
            print(f"   💸 Total Expenses: ${expenses:,.2f}")
            print(f"   🎯 Net: ${net:,.2f}")
            print()
        
        conn.close()
        
        print("✅ Data viewing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def export_to_text():
    """Export data to a text file"""
    try:
        import sys
        original_stdout = sys.stdout
        
        with open('finance_data_export.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            view_database()
            sys.stdout = original_stdout
        print("💾 Data exported to 'finance_data_export.txt'")
    except Exception as e:
        print(f"❌ Export failed: {e}")

if __name__ == "__main__":
    view_database()
    
    # Ask if user wants to export
    response = input("\n💾 Export data to file? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        export_to_text()