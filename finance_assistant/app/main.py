from flask import Flask, request, jsonify, render_template
from flask_login import login_required, current_user
from .models.user import db
from .auth.authentication import AuthenticationManager
from .banking.transaction_processor import TransactionProcessor
from .budget.budget_engine import BudgetEngine
from .chatbot.nlp_processor import NLPProcessor
from .chatbot.financial_advisor import FinancialAdvisor
from .reporting.report_generator import ReportGenerator
import os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize managers
    auth_manager = AuthenticationManager()
    transaction_processor = TransactionProcessor()
    budget_engine = BudgetEngine()
    nlp_processor = NLPProcessor()
    financial_advisor = FinancialAdvisor()
    report_generator = ReportGenerator()
    
    with app.app_context():
        # Create tables
        db.create_all()
    
    # Routes
    @app.route('/')
    def index():
        return jsonify({
            'message': 'AI-Powered Personal Finance Assistant API',
            'version': '1.0.0',
            'status': 'active'
        })
    
    @app.route('/api/register', methods=['POST'])
    def register():
        """User registration endpoint"""
        data = request.get_json()
        result = auth_manager.register_user(
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        return jsonify(result)
    
    @app.route('/api/chat', methods=['POST'])
    @login_required
    def chat():
        """Chatbot endpoint for financial queries"""
        data = request.get_json()
        user_query = data.get('query', '')
        
        # Process query with NLP
        processed_query = nlp_processor.process_query(user_query)
        
        # Get response from financial advisor
        response = financial_advisor.get_response(
            user=current_user,
            processed_query=processed_query
        )
        
        return jsonify({
            'query': user_query,
            'response': response,
            'processed_data': processed_query
        })
    
    @app.route('/api/budget/generate', methods=['POST'])
    @login_required
    def generate_budget():
        """Generate personalized budget"""
        data = request.get_json()
        income = data.get('monthly_income')
        savings_goal = data.get('savings_goal')
        
        # Get user's transactions
        transactions = current_user.transactions
        
        # Generate budget
        budget = budget_engine.generate_monthly_budget(
            user=current_user,
            historical_data=transactions,
            income=income,
            savings_goal=savings_goal
        )
        
        return jsonify({
            'budget': budget.to_dict(),
            'message': 'Budget generated successfully'
        })
    
    @app.route('/api/reports/financial-health', methods=['GET'])
    @login_required
    def generate_financial_health_report():
        """Generate financial health report"""
        report = report_generator.generate_financial_health_report(current_user)
        return jsonify(report)
    
    @app.route('/api/transactions/analyze', methods=['GET'])
    @login_required
    def analyze_spending():
        """Analyze spending patterns"""
        analysis = transaction_processor.analyze_spending_patterns(current_user.transactions)
        return jsonify(analysis)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)