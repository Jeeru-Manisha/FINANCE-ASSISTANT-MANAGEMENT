from flask import Flask, jsonify, request, render_template
import json
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'finance-assistant-secret-key'

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

# Absolute path for SQLite database file relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'finance.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[OK] Database initialized successfully!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/')
def api_info():
    return jsonify({
        'message': '🤖 AI Personal Finance Assistant API',
        'status': 'Running',
        'version': '1.0',
        'endpoints': {
            '/api/register': 'POST - Register new user',
            '/api/transactions': 'POST - Add transaction',
            '/api/analysis/<user_id>': 'GET - Get spending analysis',
            '/api/chat': 'POST - Chat with finance assistant'
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password', 'first_name', 'last_name']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            'INSERT INTO users (email, password, first_name, last_name) VALUES (?, ?, ?, ?)',
            (data['email'], data['password'], data['first_name'], data['last_name'])
        )
        
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': user_id
        })
        
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['user_id', 'amount', 'type', 'category']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO transactions (user_id, amount, type, category, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['user_id'], data['amount'], data['type'], data['category'], data.get('description', '')))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Transaction added successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/analysis/<int:user_id>')
def analyze_spending(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Get spending by category
        c.execute('''
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE user_id = ? AND type = 'expense'
            GROUP BY category
        ''', (user_id,))
        
        spending_data = c.fetchall()
        spending_by_category = {row[0]: abs(row[1]) for row in spending_data}
        
        # Get totals
        c.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = "income"', (user_id,))
        total_income = c.fetchone()[0] or 0
        
        c.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = "expense"', (user_id,))
        total_expenses = abs(c.fetchone()[0] or 0)
        
        conn.close()
        
        net_savings = total_income - total_expenses
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
        
        # Generate recommendations
        recommendations = []
        if savings_rate < 20:
            recommendations.append("💡 Try to save at least 20% of your income")
        if spending_by_category.get('Entertainment', 0) > total_expenses * 0.15:
            recommendations.append("🎯 Consider reducing entertainment expenses")
        if spending_by_category.get('Food', 0) > total_expenses * 0.25:
            recommendations.append("🍽️ Your food expenses seem high - consider meal planning")
        if total_expenses > total_income * 0.8:
            recommendations.append("⚠️ Your expenses are high relative to income - review discretionary spending")
        if not recommendations:
            recommendations.append("✅ Your financial habits look good! Keep monitoring your spending.")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'spending_by_category': spending_by_category,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': net_savings,
            'savings_rate': round(savings_rate, 2),
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        user_query = data.get('query', '').strip()
        user_id = data.get('user_id', 1)
        
        if not user_query:
            return jsonify({'success': False, 'message': 'Missing query'}), 400
            
        q_lower = user_query.lower()

        # Query database for user's actual transactions
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE user_id = ? AND type = 'expense'
            GROUP BY category
        ''', (user_id,))
        expense_rows = c.fetchall()
        spending_by_category = {row[0]: abs(row[1]) for row in expense_rows}
        
        c.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = "income"', (user_id,))
        total_income = c.fetchone()[0] or 0.0
        
        c.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = "expense"', (user_id,))
        total_expenses = abs(c.fetchone()[0] or 0.0)
        
        conn.close()
        
        net_savings = total_income - total_expenses
        savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

        # Match specific spending category in query
        matched_category = None
        for cat in spending_by_category.keys():
            if cat.lower() in q_lower:
                matched_category = cat
                break
        
        if matched_category:
            cat_amount = spending_by_category[matched_category]
            pct = round((cat_amount / total_expenses * 100), 1) if total_expenses > 0 else 0
            response = f"📊 You have spent <b>${cat_amount:,.2f}</b> on <b>{matched_category}</b>, which makes up <b>{pct}%</b> of your total expenses (${total_expenses:,.2f})."

        elif any(word in q_lower for word in ['highest', 'most', 'top expense', 'where money']):
            if spending_by_category:
                top_cat = max(spending_by_category, key=spending_by_category.get)
                top_amount = spending_by_category[top_cat]
                pct = round((top_amount / total_expenses * 100), 1) if total_expenses > 0 else 0
                response = f"🔝 Your highest spending category is <b>{top_cat}</b> at <b>${top_amount:,.2f}</b> ({pct}% of total expenses)."
            else:
                response = "You currently have no recorded expenses in the system. Click 'Add Sample Data' to load test transactions."

        elif any(word in q_lower for word in ['spend', 'expense', 'how much spent', 'total spent']):
            if total_expenses > 0:
                top_3 = sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)[:3]
                top_str = ", ".join([f"{cat}: ${amt:,.2f}" for cat, amt in top_3])
                response = f"💳 Your total recorded expenses are <b>${total_expenses:,.2f}</b>. Your top categories are: {top_str}."
            else:
                response = "You currently have $0.00 in recorded expenses."

        elif any(word in q_lower for word in ['income', 'salary', 'earned', 'earn']):
            response = f"💰 Your total recorded income is <b>${total_income:,.2f}</b>. Net savings stand at <b>${net_savings:,.2f}</b>."

        elif any(word in q_lower for word in ['save', 'saving', 'rate']):
            if total_income > 0:
                response = f"📈 Your current savings rate is <b>{savings_rate}%</b> (Net savings: <b>${net_savings:,.2f}</b> from income of <b>${total_income:,.2f}</b>). "
                if savings_rate >= 20:
                    response += "Excellent! You are maintaining a healthy savings rate above 20%."
                else:
                    response += "Try to aim for a savings rate of at least 20% by cutting discretionary spending."
            else:
                response = "No income recorded yet to calculate your savings rate."

        elif any(word in q_lower for word in ['budget', 'limit']):
            if total_income > 0:
                response = f"💡 Based on your income of <b>${total_income:,.2f}</b>, the 50/30/20 budget allocates: <b>${total_income*0.5:,.2f}</b> for Needs (50%), <b>${total_income*0.3:,.2f}</b> for Wants (30%), and <b>${total_income*0.2:,.2f}</b> for Savings (20%)."
            else:
                response = "I can help you create a budget! Based on the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings. Load your income to see your custom targets."

        elif any(word in q_lower for word in ['debt', 'loan', 'credit']):
            response = "Managing debt is crucial! Focus on paying off high-interest debt first. Consider the avalanche method (highest interest first) or snowball method (smallest balance first)."

        elif any(word in q_lower for word in ['invest', 'stock', 'return']):
            response = "For investing, consider: 1) Diversification across assets, 2) Long-term perspective, 3) Low-cost index funds, 4) Regular contributions. Remember: time in market beats timing the market!"

        elif any(word in q_lower for word in ['hello', 'hi', 'hey']):
            response = "Hello! 👋 I'm your AI finance assistant. Ask me about your spending on specific categories (e.g., Food, Rent), your total expenses, or your savings rate!"

        elif any(word in q_lower for word in ['thank', 'thanks']):
            response = "You're welcome! 😊 Let me know if you need more analysis of your finances."

        else:
            response = f"🤖 Financial Summary for User #{user_id}: Total Income = <b>${total_income:,.2f}</b>, Total Expenses = <b>${total_expenses:,.2f}</b>, Net Savings = <b>${net_savings:,.2f}</b> ({savings_rate}% savings rate). Ask me about specific categories like Food or Rent!"

        return jsonify({
            'success': True,
            'query': user_query,
            'response': response,
            'suggestions': [
                "How much did I spend on Food?",
                "What is my highest expense?",
                "What is my total spending?",
                "Give me savings tips",
                "Help me create a budget"
            ]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/sample-data', methods=['POST'])
def add_sample_data():
    """Add sample data for testing"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # First, ensure we have a user
        c.execute("SELECT COUNT(*) FROM users WHERE id = 1")
        if c.fetchone()[0] == 0:
            c.execute(
                'INSERT INTO users (email, password, first_name, last_name) VALUES (?, ?, ?, ?)',
                ('sample@example.com', 'sample123', 'Sample', 'User')
            )
        
        # Clear existing sample transactions for user 1
        c.execute('DELETE FROM transactions WHERE user_id = 1')
        
        # Add sample transactions for user 1
        sample_transactions = [
            (1, 3000, 'income', 'Salary', 'Monthly salary'),
            (1, -800, 'expense', 'Rent', 'Monthly rent'),
            (1, -300, 'expense', 'Food', 'Groceries and dining'),
            (1, -150, 'expense', 'Transport', 'Gas and public transport'),
            (1, -100, 'expense', 'Entertainment', 'Movies and subscriptions'),
            (1, -200, 'expense', 'Shopping', 'Clothes and essentials'),
            (1, -150, 'expense', 'Utilities', 'Electricity, water, internet'),
            (1, -75, 'expense', 'Healthcare', 'Medical expenses'),
            (1, 500, 'income', 'Freelance', 'Side project income')
        ]
        
        c.executemany(
            'INSERT INTO transactions (user_id, amount, type, category, description) VALUES (?, ?, ?, ?, ?)',
            sample_transactions
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sample data added successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    init_db()
    print("AI Finance Assistant starting...")
    print("Web Interface: http://localhost:5000")
    print("API Endpoints:")
    print("   GET  /                      - Web interface")
    print("   GET  /api/                  - API information")
    print("   POST /api/register          - Register new user")
    print("   POST /api/transactions      - Add transaction") 
    print("   GET  /api/analysis/<id>     - Get spending analysis")
    print("   POST /api/chat              - Chat with AI assistant")
    print("   POST /api/sample-data       - Add sample data for testing")
    print("\nOpen http://localhost:5000 in your browser to use the web interface!")
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
