import pandas as pd
from datetime import datetime, timedelta
from ..models.transaction import Transaction, TransactionCategory
import json

class TransactionProcessor:
    """Processes and analyzes financial transactions"""
    
    def __init__(self):
        self.categories = self._load_categories()
    
    def _load_categories(self):
        """Load transaction categories and keywords"""
        try:
            with open('data/categories.json', 'r') as f:
                return json.load(f)
        except:
            # Default categories if file not found
            return {
                "Food & Dining": ["restaurant", "cafe", "food", "grocery", "supermarket", "dining"],
                "Transportation": ["uber", "lyft", "taxi", "gas", "fuel", "transport", "bus", "train"],
                "Entertainment": ["movie", "netflix", "spotify", "concert", "game", "entertainment"],
                "Utilities": ["electric", "water", "gas", "internet", "phone", "utility"],
                "Shopping": ["amazon", "walmart", "target", "mall", "shopping", "store"],
                "Healthcare": ["hospital", "doctor", "pharmacy", "medical", "health"],
                "Education": ["school", "university", "course", "book", "education"],
                "Salary": ["salary", "paycheck", "income", "payment"],
                "Investment": ["stock", "investment", "dividend", "interest"],
                "Other": []
            }
    
    def categorize_transaction(self, description, amount):
        """Automatically categorize transaction based on description"""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        # Determine if it's income or expense based on amount context
        transaction_type = "income" if amount > 0 else "expense"
        
        return "Other"
    
    def analyze_spending_patterns(self, transactions, period_days=30):
        """Analyze spending patterns over a period"""
        if not transactions:
            return {}
        
        df = pd.DataFrame([t.to_dict() for t in transactions])
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Filter for the last period_days
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_transactions = df[df['transaction_date'] >= cutoff_date]
        
        # Analyze by category
        expense_analysis = recent_transactions[recent_transactions['transaction_type'] == 'expense']
        income_analysis = recent_transactions[recent_transactions['transaction_type'] == 'income']
        
        spending_by_category = expense_analysis.groupby('category')['amount'].sum().to_dict()
        total_income = income_analysis['amount'].sum()
        total_expenses = expense_analysis['amount'].sum()
        
        return {
            'spending_by_category': spending_by_category,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': total_income - total_expenses,
            'savings_rate': ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        }
    
    def detect_anomalies(self, transactions, threshold=2.0):
        """Detect unusual spending patterns"""
        if len(transactions) < 10:  # Need sufficient data
            return []
        
        df = pd.DataFrame([t.to_dict() for t in transactions])
        expense_df = df[df['transaction_type'] == 'expense']
        
        anomalies = []
        for category in expense_df['category'].unique():
            category_data = expense_df[expense_df['category'] == category]['amount']
            if len(category_data) > 5:  # Need enough data points
                mean = category_data.mean()
                std = category_data.std()
                
                if std > 0:  # Avoid division by zero
                    recent_transactions = category_data.tail(5)
                    for idx, amount in recent_transactions.items():
                        z_score = abs(amount - mean) / std
                        if z_score > threshold:
                            anomalies.append({
                                'transaction_id': idx,
                                'category': category,
                                'amount': amount,
                                'z_score': z_score,
                                'message': f'Unusually high spending in {category}'
                            })
        
        return anomalies