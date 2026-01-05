from datetime import datetime
from ..models.budget import Budget
import pandas as pd

class BudgetEngine:
    """Engine for generating and managing budgets"""
    
    def generate_monthly_budget(self, user, historical_data, income, savings_goal=None):
        """Generate personalized monthly budget based on historical spending"""
        
        # Analyze historical spending patterns
        spending_analysis = self._analyze_historical_spending(historical_data)
        
        # Calculate recommended budget allocations
        budget_allocations = self._calculate_budget_allocations(
            spending_analysis, 
            income, 
            savings_goal
        )
        
        # Create budget object
        budget = Budget(
            user_id=user.id,
            monthly_income=income,
            savings_goal=savings_goal,
            allocations=budget_allocations,
            start_date=datetime.now().replace(day=1),
            end_date=(datetime.now().replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1))
        )
        
        return budget
    
    def _analyze_historical_spending(self, transactions):
        """Analyze historical spending patterns"""
        if not transactions:
            return {}
        
        df = pd.DataFrame([t.to_dict() for t in transactions])
        expense_df = df[df['transaction_type'] == 'expense']
        
        # Calculate average monthly spending by category
        monthly_spending = expense_df.groupby('category')['amount'].mean().to_dict()
        
        return {
            'average_monthly_spending': monthly_spending,
            'total_monthly_spending': sum(monthly_spending.values()),
            'spending_categories': list(monthly_spending.keys())
        }
    
    def _calculate_budget_allocations(self, spending_analysis, income, savings_goal):
        """Calculate budget allocations based on income and goals"""
        
        # 50-30-20 rule as baseline (Needs-50%, Wants-30%, Savings-20%)
        needs_categories = ['Utilities', 'Healthcare', 'Education']
        wants_categories = ['Entertainment', 'Shopping', 'Food & Dining']
        
        allocations = {}
        total_needs = 0
        total_wants = 0
        
        # Allocate based on historical spending with 50-30-20 guidance
        for category, avg_spending in spending_analysis.get('average_monthly_spending', {}).items():
            if category in needs_categories:
                allocation = min(avg_spending * 1.1, income * 0.5)  # Cap at 50% of income
                total_needs += allocation
            elif category in wants_categories:
                allocation = min(avg_spending * 1.05, income * 0.3)  # Cap at 30% of income
                total_wants += allocation
            else:
                allocation = avg_spending
            
            allocations[category] = round(allocation, 2)
        
        # Ensure we don't exceed income
        total_allocated = sum(allocations.values())
        if total_allocated > income * 0.8:  # If allocations exceed 80% of income
            # Scale down proportionally
            scale_factor = (income * 0.8) / total_allocated
            for category in allocations:
                allocations[category] = round(allocations[category] * scale_factor, 2)
        
        return allocations
    
    def check_budget_compliance(self, current_spending, budget):
        """Check if current spending is within budget"""
        alerts = []
        
        for category, allocated in budget.allocations.items():
            current = current_spending.get(category, 0)
            utilization = (current / allocated * 100) if allocated > 0 else 0
            
            if utilization >= 90:
                alerts.append({
                    'category': category,
                    'allocated': allocated,
                    'spent': current,
                    'utilization': utilization,
                    'message': f'You have spent {utilization:.1f}% of your {category} budget'
                })
            elif utilization >= 100:
                alerts.append({
                    'category': category,
                    'allocated': allocated,
                    'spent': current,
                    'utilization': utilization,
                    'message': f'You have exceeded your {category} budget by {current - allocated:.2f}'
                })
        
        return alerts