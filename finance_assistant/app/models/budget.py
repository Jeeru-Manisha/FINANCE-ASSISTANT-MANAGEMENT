from .user import db
from datetime import datetime
import json

class Budget(db.Model):
    """Budget model for storing user budget information"""
    
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    monthly_income = db.Column(db.Float, nullable=False)
    savings_goal = db.Column(db.Float)
    allocations = db.Column(db.Text)  # JSON stored as text
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_allocations(self, allocations_dict):
        """Store allocations as JSON string"""
        self.allocations = json.dumps(allocations_dict)
    
    def get_allocations(self):
        """Retrieve allocations as dictionary"""
        return json.loads(self.allocations) if self.allocations else {}
    
    def to_dict(self):
        """Convert budget to dictionary"""
        return {
            'id': self.id,
            'monthly_income': self.monthly_income,
            'savings_goal': self.savings_goal,
            'allocations': self.get_allocations(),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Budget {self.monthly_income}>'