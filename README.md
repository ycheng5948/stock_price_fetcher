# stock_price_fetcher
fetch stock prices using yahoo finance

usage: price_fetch.py [-h] [-a ADD [ADD ...]] [-r REMOVE [REMOVE ...]] [-f] [-p PATH] [-t TICKERS] [-v]

        Stock Market Data Fetcher CLI
        -----------------------------
        A tool to manage a watchlist and fetch daily stock data to a JSON file.
        
        Examples:
          python stock_cli.py                     (View status)
          python stock_cli.py -a AAPL MSFT        (Add stocks)
          python stock_cli.py -r MSFT             (Remove stock)
          python stock_cli.py -f                  (Fetch data for watchlist)
          python stock_cli.py -f -p ./my_data.json -v  (Fetch to specific path with logs)
          python stock_cli.py -f -t ./tickers.json  (Fetch with specific tickers path)


options:
  -h, --help            show this help message and exit
  -a ADD [ADD ...], --add ADD [ADD ...]
                        Add stocks to watchlist
  -r REMOVE [REMOVE ...], --remove REMOVE [REMOVE ...]
                        Remove stocks from watchlist
  -f, --fetch           Fetch data and export JSON
  -p PATH, --path PATH  Path for output JSON
  -t TICKERS, --tickers TICKERS
                        Path for tickers JSON
  -v, --verbose         Show details
