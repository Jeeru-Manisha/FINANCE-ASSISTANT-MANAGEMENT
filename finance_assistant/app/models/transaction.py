from .user import db
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(Enum):
    FOOD = "Food & Dining"
    TRANSPORTATION = "Transportation"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    SHOPPING = "Shopping"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    SALARY = "Salary"
    INVESTMENT = "Investment"
    OTHER = "Other"

class Transaction(db.Model):
    """Transaction model for financial transactions"""
    
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Transaction {self.amount} {self.transaction_type}>'