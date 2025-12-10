"""
Financial Tracker - Core class for tracking and analyzing personal finances
"""

import csv
import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class FinancialTracker:
    """Main class for tracking and analyzing financial data"""
    
    def __init__(self, data_file: str = "examples/example.csv"):
        """
        Initialize the financial tracker with data from a file
        
        Supports CSV, JSON, and Excel (.xlsx) file formats
        
        Args:
            data_file: Path to the data file (CSV, JSON, or Excel)
        """
        self.data_file = data_file
        self.data = []
        self.income = defaultdict(float)
        self.expenses = defaultdict(float)
        self.savings = defaultdict(float)
        self.debt = defaultdict(float)
        self._visualizer = None
        
        self._load_data()
        self._categorize_data()
    
    @property
    def visualizer(self):
        """Lazy-load visualizer when needed"""
        if self._visualizer is None:
            from visualizer import FinancialVisualizer
            self._visualizer = FinancialVisualizer(self)
        return self._visualizer
    
    def _load_data(self):
        """Load financial data from file (CSV, JSON, or Excel)"""
        file_path = Path(self.data_file)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {self.data_file}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.csv':
            self._load_csv(file_path)
        elif file_ext == '.json':
            self._load_json(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            self._load_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: .csv, .json, .xlsx, .xls")
        
        print(f"Loaded {len(self.data)} financial records from {self.data_file}")
    
    def _load_csv(self, file_path: Path):
        """Load data from CSV file"""
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
    
    def _load_json(self, file_path: Path):
        """Load data from JSON file"""
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(json_data, list):
            # If it's a list of objects, use directly
            self.data = json_data
        elif isinstance(json_data, dict) and 'data' in json_data:
            # If it's wrapped in a dict with 'data' key
            self.data = json_data['data']
        elif isinstance(json_data, dict) and 'records' in json_data:
            # If it's wrapped in a dict with 'records' key
            self.data = json_data['records']
        else:
            raise ValueError("JSON file must contain a list of records or a dict with 'data' or 'records' key")
    
    def _load_excel(self, file_path: Path):
        """Load data from Excel file"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas and openpyxl are required for Excel support. Install with: pip install pandas openpyxl")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert DataFrame to list of dicts
        self.data = df.to_dict('records')
    
    def _categorize_data(self):
        """Categorize loaded data by type"""
        required_fields = ['item', 'amount', 'type', 'frequency']
        
        for i, record in enumerate(self.data):
            # Check for required fields
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                raise ValueError(f"Record {i+1} is missing required fields: {', '.join(missing_fields)}")
            
            item = str(record['item'])
            try:
                amount = float(record['amount'])
            except (ValueError, TypeError):
                raise ValueError(f"Record {i+1}: 'amount' must be a number, got {record['amount']}")
            
            record_type = str(record['type']).lower()
            frequency = str(record.get('frequency', 'monthly')).lower()
            
            # Convert to monthly amounts for consistent calculations
            monthly_amount = self._convert_to_monthly(amount, frequency)
            
            if record_type == 'income':
                self.income[item] = monthly_amount
            elif record_type == 'expense':
                self.expenses[item] = monthly_amount
            elif record_type == 'savings':
                self.savings[item] = amount  # Keep as one-time value
            elif record_type == 'debt':
                self.debt[item] = amount  # Keep as one-time value
            else:
                print(f"WARNING: Unknown type '{record_type}' for item '{item}', skipping...")
    
    def _convert_to_monthly(self, amount: float, frequency: str) -> float:
        """Convert amounts to monthly equivalent"""
        frequency_lower = frequency.lower()
        if frequency_lower == 'monthly':
            return amount
        elif frequency_lower == 'yearly':
            return amount / 12
        elif frequency_lower == 'weekly':
            return amount * 4.33  # Average weeks per month
        elif frequency_lower == 'one-time':
            return 0  # One-time items don't contribute to monthly flow
        else:
            return amount  # Default to monthly
    
    def calculate_monthly_summary(self) -> Dict:
        """Calculate monthly financial summary"""
        total_income = sum(self.income.values())
        total_expenses = sum(self.expenses.values())
        net_monthly = total_income - total_expenses
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_monthly': net_monthly,
            'savings_rate': (net_monthly / total_income * 100) if total_income > 0 else 0
        }
    
    def calculate_net_worth(self) -> float:
        """Calculate total net worth (savings - debt)"""
        total_savings = sum(self.savings.values())
        total_debt = sum(self.debt.values())
        return total_savings - total_debt
    
    def analyze_financial_health(self) -> Dict:
        """Analyze overall financial health and provide insights"""
        monthly = self.calculate_monthly_summary()
        net_worth = self.calculate_net_worth()
        total_savings = sum(self.savings.values())
        total_debt = sum(self.debt.values())
        
        # Emergency fund analysis (should be 3-6 months of expenses)
        monthly_expenses = monthly['total_expenses']
        emergency_fund = self.savings.get('Emergency Fund Balance', 0)
        months_covered = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
        
        # Debt-to-income ratio
        debt_to_income = (total_debt / monthly['total_income']) if monthly['total_income'] > 0 else 0
        
        # Savings rate assessment
        savings_rate = monthly['savings_rate']
        
        health_score = 0
        recommendations = []
        
        # Evaluate emergency fund
        if months_covered >= 6:
            health_score += 25
            recommendations.append("OK: Excellent emergency fund coverage")
        elif months_covered >= 3:
            health_score += 15
            recommendations.append("WARNING: Emergency fund is adequate but could be improved")
        else:
            recommendations.append("WARNING: Emergency fund is below recommended 3-6 months of expenses")
        
        # Evaluate savings rate
        if savings_rate >= 20:
            health_score += 25
            recommendations.append("OK: Excellent savings rate (20%+)")
        elif savings_rate >= 10:
            health_score += 15
            recommendations.append("WARNING: Good savings rate, aim for 20%+")
        else:
            recommendations.append("WARNING: Low savings rate - consider reducing expenses")
        
        # Evaluate debt
        if debt_to_income < 2:
            health_score += 25
            recommendations.append("OK: Manageable debt level")
        elif debt_to_income < 4:
            health_score += 15
            recommendations.append("WARNING: Moderate debt level - focus on paying down high-interest debt")
        else:
            recommendations.append("WARNING: High debt-to-income ratio - prioritize debt reduction")
        
        # Evaluate net worth
        if net_worth > 0:
            health_score += 25
            recommendations.append("OK: Positive net worth")
        else:
            recommendations.append("WARNING: Negative net worth - focus on building savings and reducing debt")
        
        return {
            'health_score': health_score,
            'net_worth': net_worth,
            'emergency_fund_months': months_covered,
            'debt_to_income_ratio': debt_to_income,
            'savings_rate': savings_rate,
            'recommendations': recommendations,
            'monthly_summary': monthly
        }
    
    def project_future(self, months: int = 12) -> Dict:
        """Project financial situation into the future"""
        monthly = self.calculate_monthly_summary()
        current_net_worth = self.calculate_net_worth()
        
        monthly_savings = monthly['net_monthly']
        projected_net_worth = current_net_worth + (monthly_savings * months)
        
        # Project emergency fund growth
        current_emergency = self.savings.get('Emergency Fund Balance', 0)
        emergency_contribution = self.expenses.get('Emergency Fund', 0)
        projected_emergency = current_emergency + (emergency_contribution * months)
        
        # Project retirement savings
        current_retirement = self.savings.get('Retirement Account', 0)
        retirement_contribution = self.expenses.get('Retirement Contribution', 0)
        # Assume 7% annual return (compounded monthly)
        monthly_return_rate = 0.07 / 12
        projected_retirement = current_retirement
        for _ in range(months):
            projected_retirement = projected_retirement * (1 + monthly_return_rate) + retirement_contribution
        
        return {
            'months': months,
            'current_net_worth': current_net_worth,
            'projected_net_worth': projected_net_worth,
            'monthly_savings': monthly_savings,
            'current_emergency_fund': current_emergency,
            'projected_emergency_fund': projected_emergency,
            'current_retirement': current_retirement,
            'projected_retirement': projected_retirement
        }
    
    def display_summary(self):
        """Display a comprehensive financial summary"""
        monthly = self.calculate_monthly_summary()
        health = self.analyze_financial_health()
        net_worth = self.calculate_net_worth()
        
        print("\n" + "="*60)
        print("FINANCIAL SUMMARY")
        print("="*60)
        
        print(f"\nMonthly Income: ${monthly['total_income']:,.2f}")
        print(f"Monthly Expenses: ${monthly['total_expenses']:,.2f}")
        print(f"Net Monthly: ${monthly['net_monthly']:,.2f}")
        print(f"Savings Rate: {monthly['savings_rate']:.1f}%")
        
        print(f"\nNet Worth: ${net_worth:,.2f}")
        print(f"Total Savings: ${sum(self.savings.values()):,.2f}")
        print(f"Total Debt: ${sum(self.debt.values()):,.2f}")
        
        print(f"\nFinancial Health Score: {health['health_score']}/100")
        print(f"Emergency Fund Coverage: {health['emergency_fund_months']:.1f} months")
        print(f"Debt-to-Income Ratio: {health['debt_to_income_ratio']:.2f}")
        
        print("\nRecommendations:")
        for rec in health['recommendations']:
            print(f"   {rec}")
        
        # Future projections
        future = self.project_future(12)
        print(f"\n12-Month Projections:")
        print(f"   Projected Net Worth: ${future['projected_net_worth']:,.2f}")
        print(f"   Projected Emergency Fund: ${future['projected_emergency_fund']:,.2f}")
        print(f"   Projected Retirement: ${future['projected_retirement']:,.2f}")
    
    def plot_expenses(self, save_path: str = None):
        """Create a pie chart of expenses (delegates to visualizer)"""
        return self.visualizer.plot_expenses(save_path)
    
    def plot_income_vs_expenses(self, save_path: str = None):
        """Create a bar chart comparing income and expenses (delegates to visualizer)"""
        return self.visualizer.plot_income_vs_expenses(save_path)
    
    def plot_future_projection(self, months: int = 12, save_path: str = None):
        """Plot future financial projections (delegates to visualizer)"""
        return self.visualizer.plot_future_projection(months, save_path)
    
    def create_web_dashboard(self, output_path: str = None, open_browser: bool = True):
        """Create an interactive web dashboard (delegates to visualizer)"""
        return self.visualizer.create_web_dashboard(output_path, open_browser)

