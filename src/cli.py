"""
CLI entry point for Weekend Financier
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path
from financial_tracker import FinancialTracker


class TeeOutput:
    """Class that writes to both console and file"""
    def __init__(self, *files):
        self.files = files
    
    def write(self, text):
        for f in self.files:
            f.write(text)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                  WEEKEND FINANCIER                        ║
║                                                           ║
║          "For when the week's not long enough"            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""


def init(data_file: str = None):
    """
    Initialize the financial tracker application
    
    Args:
        data_file: Path to the data file (CSV, JSON, or Excel) containing financial data (optional)
    
    Returns:
        FinancialTracker instance
    """
    print("Initializing Financial Tracker...")
    
    # Use default if not provided
    if data_file is None:
        data_file = "examples/example.csv"
    
    tracker = FinancialTracker(data_file)
    return tracker


def main():
    """Main CLI entry point"""
    # Print banner
    print(BANNER)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Financial Tracker - Analyze your personal finances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  financier                                    # Use default file
  financier examples/example.csv               # CSV file
  financier examples/example.json              # JSON file
  financier examples/example.xlsx              # Excel file
  financier --snapshot                          # Save charts with date suffix
  financier --output-dir reports/               # Save to custom directory
  financier --no-dashboard                     # Skip web dashboard
  financier --no-charts                        # Skip PNG charts
        """
    )
    parser.add_argument(
        'data_file',
        nargs='?',
        default=None,
        help='Path to data file (CSV, JSON, or Excel) with financial data (default: examples/example.csv)'
    )
    parser.add_argument(
        '--no-dashboard',
        action='store_true',
        help='Skip generating web dashboard'
    )
    parser.add_argument(
        '--no-charts',
        action='store_true',
        help='Skip generating PNG charts'
    )
    parser.add_argument(
        '--snapshot',
        action='store_true',
        help='Append date to chart filenames for snapshot (e.g., expenses_chart_2024-01-15.png)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Save charts to custom directory (default: reports/)'
    )
    
    args = parser.parse_args()
    
    # Determine data file to use
    data_file = args.data_file or "examples/example.csv"
    
    if data_file == "examples/example.csv":
        print(f"Using default file: {data_file}")
    else:
        print(f"Using file: {data_file}")
    
    # Check if dependencies are installed
    print("Checking dependencies...")
    missing_deps = []
    
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
    
    try:
        import plotly
    except ImportError:
        missing_deps.append("plotly")
    
    if missing_deps:
        print(f"WARNING: Missing dependencies: {', '.join(missing_deps)}")
        print("   Install with: pip install -r requirements.txt")
        print("   The program will still run, but visualization features will be limited.\n")
    
    # Determine output directory and filename format
    # Default to reports/ folder to keep project root clean
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path("reports")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename suffix if taking a snapshot
    date_suffix = ""
    if args.snapshot:
        date_suffix = "_" + datetime.now().strftime("%Y-%m-%d")
    
    # Set up output logging to file
    log_file_path = output_dir / f"financial_report{date_suffix}.txt"
    log_file = open(log_file_path, 'w', encoding='utf-8')
    
    # Save original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Create TeeOutput to write to both console and file
    tee_stdout = TeeOutput(sys.stdout, log_file)
    tee_stderr = TeeOutput(sys.stderr, log_file)
    
    # Redirect stdout and stderr
    sys.stdout = tee_stdout
    sys.stderr = tee_stderr
    
    try:
        print(f"Saving charts to: {output_dir}/")
        
        if args.snapshot:
            print(f"Taking snapshot - appending date to filenames: {date_suffix}")
        
        # Initialize the application
        tracker = init(data_file)
        
        # Display summary
        tracker.display_summary()
        
        # Create visualizations
        if not args.no_charts:
            print("\nGenerating visualizations...")
            
            # Option 1: Static PNG charts
            expenses_path = output_dir / f"expenses_chart{date_suffix}.png"
            income_path = output_dir / f"income_vs_expenses{date_suffix}.png"
            projection_path = output_dir / f"future_projection{date_suffix}.png"
            
            tracker.plot_expenses(str(expenses_path))
            tracker.plot_income_vs_expenses(str(income_path))
            tracker.plot_future_projection(12, str(projection_path))
        
        # Option 2: Interactive web dashboard
        if not args.no_dashboard:
            print("\nCreating web dashboard...")
            dashboard_path = output_dir / f"financial_dashboard{date_suffix}.html"
            tracker.create_web_dashboard(str(dashboard_path), open_browser=False)
            print(f"   Open {dashboard_path} in your browser to view it.")
        
        print("\nFinancial analysis complete!")
        print(f"Report saved to: {log_file_path}")
    
    finally:
        # Restore original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()


if __name__ == "__main__":
    main()
