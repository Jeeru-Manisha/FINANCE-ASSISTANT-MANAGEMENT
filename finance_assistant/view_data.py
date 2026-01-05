import sqlite3
import pandas as pd
from datetime import datetime

def view_database():
    print("🔍 VIEWING FINANCE DATABASE")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('finance.db')
        
        # View Users
        print("\n👥 USERS TABLE:")
        users_df = pd.read_sql_query("SELECT * FROM users", conn)
        if not users_df.empty:
            print(users_df.to_string(index=False))
        else:
            print("No users found")
        
        # View Transactions
        print("\n💳 TRANSACTIONS TABLE:")
        transactions_df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
        if not transactions_df.empty:
            print(transactions_df.to_string(index=False))
        else:
            print("No transactions found")
        
        # View Spending Summary
        print("\n📊 SPENDING SUMMARY:")
        summary_df = pd.read_sql_query('''
            SELECT 
                type,
                category,
                COUNT(*) as count,
                SUM(amount) as total,
                AVG(amount) as average
            FROM transactions 
            GROUP BY type, category
            ORDER BY type, total DESC
        ''', conn)
        if not summary_df.empty:
            print(summary_df.to_string(index=False))
        else:
            print("No data for summary")
        
        # Financial Health
        print("\n❤️ FINANCIAL HEALTH:")
        health_df = pd.read_sql_query('''
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expenses,
                SUM(amount) as net_savings
            FROM transactions
        ''', conn)
        if not health_df.empty:
            print(health_df.to_string(index=False))
            
            total_income = health_df['total_income'].iloc[0] or 0
            total_expenses = abs(health_df['total_expenses'].iloc[0] or 0)
            net_savings = health_df['net_savings'].iloc[0] or 0
            
            if total_income > 0:
                savings_rate = (net_savings / total_income) * 100
                print(f"\n💡 Savings Rate: {savings_rate:.1f}%")
            
            if net_savings >= 0:
                print("✅ Good job! You're saving money.")
            else:
                print("⚠️ Warning: You're spending more than you earn.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_database()