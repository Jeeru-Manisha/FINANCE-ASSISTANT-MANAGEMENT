from ..banking.transaction_processor import TransactionProcessor
from ..budget.budget_engine import BudgetEngine
import random

class FinancialAdvisor:
    """Financial advisor chatbot that provides intelligent responses"""
    
    def __init__(self):
        self.transaction_processor = TransactionProcessor()
        self.budget_engine = BudgetEngine()
    
    def get_response(self, user, processed_query):
        """Generate response based on processed user query"""
        intent = processed_query.get('intent')
        entities = processed_query.get('entities', {})
        
        if intent == 'get_spending_summary':
            return self._get_spending_summary(user, entities)
        elif intent == 'get_budget_status':
            return self._get_budget_status(user, entities)
        elif intent == 'get_savings_advice':
            return self._get_savings_advice(user, entities)
        elif intent == 'get_income_report':
            return self._get_income_report(user, entities)
        elif intent == 'get_financial_report':
            return self._get_financial_report(user, entities)
        else:
            return self._get_general_response(processed_query)
    
    def _get_spending_summary(self, user, entities):
        """Generate spending summary response"""
        analysis = self.transaction_processor.analyze_spending_patterns(user.transactions)
        
        if not analysis:
            return "I don't have enough transaction data to analyze your spending patterns."
        
        total_spent = analysis.get('total_expenses', 0)
        top_category = max(analysis.get('spending_by_category', {}).items(), 
                          key=lambda x: x[1], default=('None', 0))
        
        responses = [
            f"Based on your recent transactions, you've spent ${total_spent:.2f}. "
            f"Your highest spending category is {top_category[0]} at ${top_category[1]:.2f}.",
            
            f"Your spending analysis shows total expenses of ${total_spent:.2f}. "
            f"Consider reviewing your {top_category[0]} expenses which are at ${top_category[1]:.2f}.",
            
            f"Here's your spending summary: Total expenses: ${total_spent:.2f}. "
            f"Top category: {top_category[0]} (${top_category[1]:.2f})."
        ]
        
        return random.choice(responses)
    
    def _get_budget_status(self, user, entities):
        """Generate budget status response"""
        if not user.budgets:
            return "You haven't set up any budgets yet. Would you like me to help you create one?"
        
        current_budget = user.budgets[-1]  # Get most recent budget
        spending_analysis = self.transaction_processor.analyze_spending_patterns(user.transactions)
        
        alerts = self.budget_engine.check_budget_compliance(
            spending_analysis.get('spending_by_category', {}), 
            current_budget
        )
        
        if alerts:
            alert_msg = " | ".join([alert['message'] for alert in alerts[:2]])
            return f"Budget alerts: {alert_msg}"
        else:
            return "Great! You're staying within your budget limits. Keep up the good financial habits!"
    
    def _get_savings_advice(self, user, entities):
        """Generate savings advice"""
        analysis = self.transaction_processor.analyze_spending_patterns(user.transactions)
        savings_rate = analysis.get('savings_rate', 0)
        
        if savings_rate >= 20:
            return "Excellent! Your savings rate is strong. Consider investment options for better returns."
        elif savings_rate >= 10:
            return "Good savings habits! You could optimize further by reviewing discretionary spending."
        else:
            return "Let's work on improving your savings. Try reducing dining out or entertainment expenses."
    
    def _get_income_report(self, user, entities):
        """Generate income report"""
        analysis = self.transaction_processor.analyze_spending_patterns(user.transactions)
        total_income = analysis.get('total_income', 0)
        
        return f"Your total income from the analyzed period is ${total_income:.2f}."
    
    def _get_financial_report(self, user, entities):
        """Generate financial report summary"""
        analysis = self.transaction_processor.analyze_spending_patterns(user.transactions)
        
        return (
            f"Financial Summary:\n"
            f"Income: ${analysis.get('total_income', 0):.2f}\n"
            f"Expenses: ${analysis.get('total_expenses', 0):.2f}\n"
            f"Net Savings: ${analysis.get('net_savings', 0):.2f}\n"
            f"Savings Rate: {analysis.get('savings_rate', 0):.1f}%"
        )
    
    def _get_general_response(self, processed_query):
        """Generate general responses"""
        general_responses = [
            "I can help you with budgeting, spending analysis, savings advice, and financial reports.",
            "Ask me about your spending patterns, budget status, or savings goals!",
            "I'm here to help with your financial questions. Try asking about your budget or spending.",
            "You can ask me to analyze your transactions, check budget compliance, or get savings tips."
        ]
        
        return random.choice(general_responses)