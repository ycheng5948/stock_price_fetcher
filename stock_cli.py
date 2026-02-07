import yfinance as yf
import json
import os
import argparse
import sys
from datetime import datetime
from colorama import *

# --- Configuration ---
TICKER_FILE = 'tickers.json'
DEFAULT_OUTPUT_FILE = 'stock_data.json'

def load_tickers():
    """Loads the list of stock tickers from a JSON file."""
    if not os.path.exists(TICKER_FILE):
        return []
    with open(TICKER_FILE, 'r') as f:
        return json.load(f)

def save_tickers(ticker_list):
    """Saves the list of stock tickers to a JSON file."""
    # Deduplicate and sort
    clean_list = sorted(list(set([t.upper() for t in ticker_list])))
    with open(TICKER_FILE, 'w') as f:
        json.dump(clean_list, f)

def get_last_update_time(file_path):
    """Gets the human-readable last modified time of a file."""
    if os.path.exists(file_path):
        mod_time = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
    return "Never (File not found)"

def log(message, is_verbose):
    """Prints message only if verbose mode is on."""
    if is_verbose:
        print(f"[INFO] {message}")

def fetch_data(tickers, output_path, is_verbose):
    """Fetches stock data and saves to JSON."""
    if not tickers:
        # print("Error: Watchlist is empty. Use -a to add stocks.")
        print(Fore.LIGHTRED_EX + "Error: Watchlist is empty. Use -a to add stocks." + Fore.RESET)
        return

    log(f"Connecting to Yahoo Finance API...", is_verbose)
    log(f"Querying: {', '.join(tickers)}", is_verbose)
    
    # Fetch data
    try:
        # group_by='ticker' ensures consistent formatting even for single stocks
        data = yf.download(tickers, period="1d", group_by='ticker', progress=False)
    except Exception as e:
        # print(f"Error: Network or API failure: {e}")
        print(Fore.LIGHTRED_EX + f"Error: Network or API failure: {e}" + Fore.RESET)
        return

    results = []
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log("Processing data points...", is_verbose)

    # Convert single ticker string to list if necessary for iteration
    if isinstance(tickers, str):
        tickers = [tickers]

    for ticker in tickers:
        try:
            # Handle Data Structure (DataFrame vs Series depending on yf version/count)
            if len(tickers) == 1:
                stock_data = data
            else:
                stock_data = data[ticker]
            
            if stock_data.empty:
                log(f"Warning: No data found for {ticker}", is_verbose)
                continue

            # Get the last available row (most recent data)
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
            # log(f"Error parsing {ticker}: {e}", is_verbose)
            print(Fore.LIGHTRED_EX + f"Error parsing {ticker}: {e}", is_verbose + Fore.RESET)
            

    # Save to file
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        # print(f"Success. Data for {len(results)} stocks exported to:")
        print(Fore.LIGHTGREEN_EX + f"Success. Data for {len(results)} stocks exported to:")
        print(f"-> {output_path}" + Fore.RESET)
    except IOError as e:
        # print(f"Error writing to file: {e}")
        print(Fore.LIGHTRED_EX + f"Error writing to file: {e}" + Fore.RESET)

def main():
    parser = argparse.ArgumentParser(
        description="""
        Stock Market Data Fetcher CLI
        -----------------------------
        A tool to manage a watchlist and fetch daily stock data to a JSON file.
        
        Examples:
          python stock_cli.py                     (View status)
          python stock_cli.py -a AAPL MSFT        (Add stocks)
          python stock_cli.py -r MSFT             (Remove stock)
          python stock_cli.py -f                  (Fetch data for watchlist)
          python stock_cli.py -f -p ./my_data.json -v  (Fetch to specific path with logs)
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Arguments
    parser.add_argument('-a', '--add', nargs='+', help='Add one or more stock symbols to watchlist')
    parser.add_argument('-r', '--remove', nargs='+', help='Remove one or more stock symbols')
    parser.add_argument('-f', '--fetch', action='store_true', help='Fetch current stock data and export JSON')
    parser.add_argument('-p', '--path', type=str, default=DEFAULT_OUTPUT_FILE, help=f'Custom output path for JSON (Default: {DEFAULT_OUTPUT_FILE})')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed processing information')

    args = parser.parse_args()
    
    # --- CHANGE: Convert path to Absolute Path immediately ---
    args.path = os.path.abspath(args.path)
    
    # Load current list
    current_tickers = load_tickers()

    # Priority 1: Modification Actions
    if args.add:
        log(f"Adding: {args.add}", args.verbose)
        for t in args.add:
            current_tickers.append(t.upper())
        save_tickers(current_tickers)
        print(f"Updated Watchlist: {load_tickers()}")
        return

    if args.remove:
        log(f"Removing: {args.remove}", args.verbose)
        for t in args.remove:
            t = t.upper()
            if t in current_tickers:
                current_tickers.remove(t)
            else:
                print(f"Warning: {t} was not in the list.")
        save_tickers(current_tickers)
        print(f"Updated Watchlist: {load_tickers()}")
        return

    # Priority 2: Fetch Action
    if args.fetch:
        fetch_data(current_tickers, args.path, args.verbose)
        return

    # Priority 3: Default View (No args provided)
    # If no flags are set, show status
    print("-" * 60)
    print("STOCK WATCHLIST STATUS")
    print("-" * 60)
    if current_tickers:
        print(f"Tickers ({len(current_tickers)}): {', '.join(current_tickers)}")
    else:
        print("Tickers: [Empty List]")
    
    print("-" * 60)
    print(f"Last Data Export: {get_last_update_time(args.path)}")
    print(f"Export Path:      {args.path}")
    print("-" * 60)
    print("Tip: Use -h for help on how to fetch data or edit list.")

if __name__ == "__main__":
    main()