import json
import os
import argparse
import sys
from datetime import datetime

# --- Smart Defaults ---
# This line finds the folder where THIS .py file is actually saved
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TICKER_FILE = os.path.join(SCRIPT_DIR, 'tickers.json')
DEFAULT_OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'stock_data.json')

def load_tickers(file_path):
    """Loads the list of stock tickers from a JSON file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        return json.load(f)

def save_tickers(ticker_list, file_path):
    """Saves the list of stock tickers to a JSON file."""
    clean_list = sorted(list(set([t.upper() for t in ticker_list])))
    with open(file_path, 'w') as f:
        json.dump(clean_list, f)

def get_last_update_time(file_path):
    if os.path.exists(file_path):
        mod_time = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
    return "Never (File not found)"

def log(message, is_verbose):
    if is_verbose:
        print(f"[INFO] {message}")

def fetch_data(tickers, output_path, is_verbose):
    if not tickers:
        print("Error: Watchlist is empty. Use -a to add stocks.")
        return

    log(f"Connecting to Yahoo Finance API...", is_verbose)
    
    try:
        data = yf.download(tickers, period="1d", group_by='ticker', progress=False)
    except Exception as e:
        print(f"Error: Network or API failure: {e}")
        return

    results = []
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Force tickers into a list if it's a single string
    ticker_list = [tickers] if isinstance(tickers, str) else tickers

    for ticker in ticker_list:
        try:
            stock_data = data if len(ticker_list) == 1 else data[ticker]
            
            if stock_data.empty:
                log(f"Warning: No data found for {ticker}", is_verbose)
                continue

            row = stock_data.iloc[-1]
            info = {
                "symbol": ticker,
                "fetch_timestamp": timestamp_str,
                "market_date": str(row.name.date()),
                "open": round(float(row['Open']), 2),
                "close": round(float(row['Close']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
            }
            results.append(info)
            log(f"Processed {ticker}: ${info['close']}", is_verbose)
        except Exception as e:
            log(f"Error parsing {ticker}: {e}", is_verbose)

    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Success. Data for {len(results)} stocks exported to:\n-> {output_path}")
    except IOError as e:
        print(f"Error writing to file: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Stock Market Data Fetcher CLI",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-a', '--add', nargs='+', help='Add stocks to watchlist')
    parser.add_argument('-r', '--remove', nargs='+', help='Remove stocks from watchlist')
    parser.add_argument('-f', '--fetch', action='store_true', help='Fetch data and export JSON')
    parser.add_argument('-p', '--path', type=str, default=DEFAULT_OUTPUT_FILE, help='Path for output JSON')
    parser.add_argument('-t', '--tickers', type=str, default=DEFAULT_TICKER_FILE, help='Path for tickers JSON')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show details')

    args = parser.parse_args()
    
    # Convert both paths to Absolute Paths
    args.path = os.path.abspath(args.path)
    args.tickers = os.path.abspath(args.tickers)
    
    # Load list from the specified ticker path
    current_tickers = load_tickers(args.tickers)

    if args.add:
        for t in args.add:
            current_tickers.append(t.upper())
        save_tickers(current_tickers, args.tickers)
        print(f"Updated Watchlist ({args.tickers}):\n{load_tickers(args.tickers)}")
        return

    if args.remove:
        for t in args.remove:
            t = t.upper()
            if t in current_tickers: current_tickers.remove(t)
        save_tickers(current_tickers, args.tickers)
        print(f"Updated Watchlist ({args.tickers}):\n{load_tickers(args.tickers)}")
        return

    if args.fetch:
        fetch_data(current_tickers, args.path, args.verbose)
        return

    # Default Status View
    print("-" * 60)
    print("STOCK WATCHLIST STATUS")
    print("-" * 60)
    print(f"Tickers Path:     {args.tickers}")
    print(f"Tickers ({len(current_tickers)}): {', '.join(current_tickers) if current_tickers else '[Empty]'}")
    print("-" * 60)
    print(f"Last Data Export: {get_last_update_time(args.path)}")
    print(f"Export Path:      {args.path}")
    print("-" * 60)

if __name__ == "__main__":
    main()
