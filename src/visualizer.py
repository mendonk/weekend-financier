"""
Visualization module for financial data
Supports both static matplotlib charts and interactive web dashboards
"""

from typing import Dict, Optional
from pathlib import Path

# Optional imports - will raise helpful errors when used if not installed
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None


class FinancialVisualizer:
    """Handles visualization of financial data"""
    
    def __init__(self, tracker):
        """
        Initialize visualizer with a FinancialTracker instance
        
        Args:
            tracker: FinancialTracker instance to visualize
        """
        self.tracker = tracker
    
    def plot_expenses(self, save_path: Optional[str] = None):
        """Create a pie chart of expenses using matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            print("ERROR: matplotlib is not installed. Install it with: pip install matplotlib")
            return
        
        if not self.tracker.expenses:
            print("No expense data to plot")
            return
        
        labels = list(self.tracker.expenses.keys())
        values = list(self.tracker.expenses.values())
        
        plt.figure(figsize=(10, 8))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Monthly Expenses Breakdown', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        else:
            plt.show()
        plt.close()
    
    def plot_income_vs_expenses(self, save_path: Optional[str] = None):
        """Create a bar chart comparing income and expenses using matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            print("ERROR: matplotlib is not installed. Install it with: pip install matplotlib")
            return
        
        monthly = self.tracker.calculate_monthly_summary()
        
        categories = ['Income', 'Expenses', 'Net']
        amounts = [
            monthly['total_income'],
            monthly['total_expenses'],
            monthly['net_monthly']
        ]
        colors = ['green', 'red', 'blue' if monthly['net_monthly'] >= 0 else 'orange']
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories, amounts, color=colors, alpha=0.7)
        plt.title('Monthly Income vs Expenses', fontsize=16, fontweight='bold')
        plt.ylabel('Amount ($)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'${amount:,.0f}',
                    ha='center', va='bottom' if amount >= 0 else 'top')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        else:
            plt.show()
        plt.close()
    
    def plot_future_projection(self, months: int = 12, save_path: Optional[str] = None):
        """Plot future financial projections using matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            print("ERROR: matplotlib is not installed. Install it with: pip install matplotlib")
            return
        
        monthly = self.tracker.calculate_monthly_summary()
        
        # Generate monthly data points
        months_list = list(range(0, months + 1))
        net_worth_projection = []
        emergency_projection = []
        retirement_projection = []
        
        current_net = self.tracker.calculate_net_worth()
        current_emergency = self.tracker.savings.get('Emergency Fund Balance', 0)
        current_retirement = self.tracker.savings.get('Retirement Account', 0)
        emergency_contrib = self.tracker.expenses.get('Emergency Fund', 0)
        retirement_contrib = self.tracker.expenses.get('Retirement Contribution', 0)
        monthly_return_rate = 0.07 / 12
        
        for month in months_list:
            net_worth_projection.append(current_net + (monthly['net_monthly'] * month))
            emergency_projection.append(current_emergency + (emergency_contrib * month))
            
            # Compound retirement growth
            retirement = current_retirement
            for m in range(month):
                retirement = retirement * (1 + monthly_return_rate) + retirement_contrib
            retirement_projection.append(retirement)
        
        plt.figure(figsize=(12, 8))
        plt.plot(months_list, net_worth_projection, label='Net Worth', linewidth=2, marker='o')
        plt.plot(months_list, emergency_projection, label='Emergency Fund', linewidth=2, marker='s')
        plt.plot(months_list, retirement_projection, label='Retirement Account', linewidth=2, marker='^')
        
        plt.title(f'{months}-Month Financial Projection', fontsize=16, fontweight='bold')
        plt.xlabel('Months', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xticks(months_list[::max(1, months//12)])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        else:
            plt.show()
        plt.close()
    
    def create_web_dashboard(self, output_path: Optional[str] = None, open_browser: bool = False):
        """
        Create an interactive web dashboard with all financial charts
        
        Args:
            output_path: Path to save HTML file (default: financial_dashboard.html)
            open_browser: Whether to automatically open in browser (default: False)
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            print("Plotly not installed. Install with: pip install plotly")
            print("Falling back to static charts...")
            return
        
        monthly = self.tracker.calculate_monthly_summary()
        health = self.tracker.analyze_financial_health()
        future = self.tracker.project_future(12)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Income vs Expenses', 'Expense Breakdown', 
                          '12-Month Projection', 'Financial Health'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter", "colspan": 2}, None]],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # 1. Income vs Expenses Bar Chart
        categories = ['Income', 'Expenses', 'Net']
        amounts = [
            monthly['total_income'],
            monthly['total_expenses'],
            monthly['net_monthly']
        ]
        colors_bar = ['#2ecc71', '#e74c3c', '#3498db' if monthly['net_monthly'] >= 0 else '#f39c12']
        
        fig.add_trace(
            go.Bar(x=categories, y=amounts, marker_color=colors_bar, 
                   text=[f'${a:,.0f}' for a in amounts], textposition='outside',
                   name='Monthly Flow'),
            row=1, col=1
        )
        
        # 2. Expense Pie Chart
        if self.tracker.expenses:
            expense_labels = list(self.tracker.expenses.keys())
            expense_values = list(self.tracker.expenses.values())
            fig.add_trace(
                go.Pie(labels=expense_labels, values=expense_values, 
                       name="Expenses", hole=0.3),
                row=1, col=2
            )
        
        # 3. Future Projection
        months_list = list(range(0, 13))
        current_net = self.tracker.calculate_net_worth()
        current_emergency = self.tracker.savings.get('Emergency Fund Balance', 0)
        current_retirement = self.tracker.savings.get('Retirement Account', 0)
        emergency_contrib = self.tracker.expenses.get('Emergency Fund', 0)
        retirement_contrib = self.tracker.expenses.get('Retirement Contribution', 0)
        monthly_return_rate = 0.07 / 12
        
        net_worth_proj = []
        emergency_proj = []
        retirement_proj = []
        
        for month in months_list:
            net_worth_proj.append(current_net + (monthly['net_monthly'] * month))
            emergency_proj.append(current_emergency + (emergency_contrib * month))
            retirement = current_retirement
            for m in range(month):
                retirement = retirement * (1 + monthly_return_rate) + retirement_contrib
            retirement_proj.append(retirement)
        
        fig.add_trace(
            go.Scatter(x=months_list, y=net_worth_proj, mode='lines+markers',
                      name='Net Worth', line=dict(color='#3498db', width=3)),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=months_list, y=emergency_proj, mode='lines+markers',
                      name='Emergency Fund', line=dict(color='#2ecc71', width=3)),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=months_list, y=retirement_proj, mode='lines+markers',
                      name='Retirement', line=dict(color='#9b59b6', width=3)),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title_text="Financial Dashboard",
            title_x=0.5,
            title_font_size=24,
            showlegend=True,
            height=900,
            template="plotly_white"
        )
        
        # Update axes
        fig.update_xaxes(title_text="Category", row=1, col=1)
        fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_xaxes(title_text="Months", row=2, col=1)
        fig.update_yaxes(title_text="Amount ($)", row=2, col=1)
        
        # Determine health score color
        health_color = (
            'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' if health['health_score'] >= 75 
            else 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' if health['health_score'] < 50
            else 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)'
        )
        
        # Convert figure to JSON
        import json
        figure_json = json.dumps(fig.to_dict())
        
        # Create recommendations HTML
        rec_html = "".join([f"<li>{rec}</li>" for rec in health['recommendations']])
        
        # Create HTML with summary
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Financial Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .summary-card .value {{
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }}
        .health-score {{
            background: {health_color};
        }}
        .recommendations {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .recommendations h3 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .recommendations ul {{
            list-style: none;
            padding: 0;
        }}
        .recommendations li {{
            padding: 8px 0;
            border-bottom: 1px solid #bdc3c7;
        }}
        .recommendations li:last-child {{
            border-bottom: none;
        }}
        #chart {{
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Financial Dashboard</h1>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Monthly Income</h3>
                <p class="value">${monthly['total_income']:,.0f}</p>
            </div>
            <div class="summary-card">
                <h3>Monthly Expenses</h3>
                <p class="value">${monthly['total_expenses']:,.0f}</p>
            </div>
            <div class="summary-card">
                <h3>Net Monthly</h3>
                <p class="value">${monthly['net_monthly']:,.0f}</p>
            </div>
            <div class="summary-card">
                <h3>Savings Rate</h3>
                <p class="value">{monthly['savings_rate']:.1f}%</p>
            </div>
            <div class="summary-card health-score">
                <h3>Health Score</h3>
                <p class="value">{health['health_score']}/100</p>
            </div>
            <div class="summary-card">
                <h3>Net Worth</h3>
                <p class="value">${health['net_worth']:,.0f}</p>
            </div>
        </div>
        
        <div id="chart"></div>
        
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ul>
                {rec_html}
            </ul>
        </div>
    </div>
    
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        var figure = {figure_json};
        Plotly.newPlot('chart', figure.data, figure.layout, {{responsive: true}});
    </script>
</body>
</html>
"""
        
        # Save HTML
        if output_path is None:
            output_path = Path("financial_dashboard.html")
        else:
            output_path = Path(output_path)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Web dashboard saved to: {output_path.absolute()}")
        
        if open_browser:
            try:
                import webbrowser
                webbrowser.open(f"file://{output_path.absolute()}")
                print("Opening dashboard in browser...")
            except Exception as e:
                print(f"WARNING: Could not open browser automatically: {e}")
                print(f"   Please open the file manually: {output_path.absolute()}")
        
        return str(output_path)

