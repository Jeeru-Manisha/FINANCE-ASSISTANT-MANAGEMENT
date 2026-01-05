import pandas as pd
from datetime import datetime
import json

class ReportGenerator:
    """Generates financial reports in various formats"""
    
    def generate_financial_health_report(self, user):
        """Generate comprehensive financial health report"""
        transactions = user.transactions
        
        if not transactions:
            return {"error": "No transaction data available"}
        
        # Analyze financial data
        analysis = self._analyze_financial_health(transactions)
        
        report = {
            "user": {
                "name": user.get_full_name(),
                "email": user.email
            },
            "report_date": datetime.now().isoformat(),
            "period": "Last 30 days",
            "financial_metrics": analysis,
            "recommendations": self._generate_recommendations(analysis)
        }
        
        return report
    
    def _analyze_financial_health(self, transactions):
        """Analyze financial health metrics"""
        df = pd.DataFrame([t.to_dict() for t in transactions])
        
        # Basic metrics
        total_income = df[df['transaction_type'] == 'income']['amount'].sum()
        total_expenses = df[df['transaction_type'] == 'expense']['amount'].sum()
        net_savings = total_income - total_expenses
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
        
        # Spending by category
        spending_by_category = df[df['transaction_type'] == 'expense'].groupby('category')['amount'].sum().to_dict()
        
        # Monthly trends (simplified)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        monthly_trends = df.groupby(df['transaction_date'].dt.to_period('M'))['amount'].sum()
        
        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate": round(savings_rate, 2),
            "spending_by_category": spending_by_category,
            "monthly_trends": monthly_trends.to_dict()
        }
    
    def _generate_recommendations(self, analysis):
        """Generate personalized financial recommendations"""
        recommendations = []
        
        savings_rate = analysis.get('savings_rate', 0)
        total_expenses = analysis.get('total_expenses', 0)
        
        if savings_rate < 10:
            recommendations.append("Consider increasing your savings rate to at least 20% for better financial security.")
        
        if analysis.get('spending_by_category', {}).get('Entertainment', 0) > total_expenses * 0.15:
            recommendations.append("Your entertainment spending seems high. Consider setting a monthly limit.")
        
        if savings_rate > 20:
            recommendations.append("Great savings rate! Consider exploring investment options for higher returns.")
        
        if not recommendations:
            recommendations.append("Your financial habits look good. Continue monitoring your spending regularly.")
        
        return recommendations
    
    def export_report_pdf(self, report_data, filename):
        """Export report as PDF (simplified implementation)"""
        # In a real implementation, this would use ReportLab to generate PDF
        print(f"PDF report generated: {filename}")
        return {"status": "PDF export functionality would be implemented here"}
    
    def export_report_excel(self, report_data, filename):
        """Export report as Excel (simplified implementation)"""
        # In a real implementation, this would use openpyxl to generate Excel
        print(f"Excel report generated: {filename}")
        return {"status": "Excel export functionality would be implemented here"}