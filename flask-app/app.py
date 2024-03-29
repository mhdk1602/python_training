from flask import Flask, request, jsonify
from datetime import datetime
import yfinance as yf
import requests
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GRAPHQL_ENDPOINT = "http://hasura:8080/v1/graphql"
HASURA_ADMIN_SECRET = os.getenv('HASURA_ADMIN_SECRET').strip('"')

def get_stock_price(symbol):
    now = datetime.utcnow()
    market_open = now.replace(hour=13, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=20, minute=0, second=0, microsecond=0)

    ticker = yf.Ticker(symbol)
    if market_open <= now <= market_close:
        price = ticker.history(period="1d")["Close"].iloc[-1]
    elif now > market_close:
        price = ticker.history(period="1d")["Close"].iloc[-1]
    else:
        price = ticker.history(period="2d")["Close"].iloc[-2]
    
    return price

def format_market_cap(market_cap):
    if market_cap >= 1e12:
        return f"{market_cap / 1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"{market_cap / 1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"{market_cap / 1e6:.2f}M"
    else:
        return f"{market_cap:.2f}"

def fetch_yfinance_overview(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    market_cap = info.get("marketCap")
    formatted_market_cap = format_market_cap(market_cap) if market_cap else "N/A"
    as_of_date = datetime.utcnow().strftime('%Y-%m-%d')
    
    return {
        "ticker": symbol,
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": formatted_market_cap,
        "description": info.get("longBusinessSummary", "N/A"),
        "as_of_date": as_of_date
    }

def execute_graphql(query, variables=None):
    response = requests.post(
        GRAPHQL_ENDPOINT, 
        json={'query': query, 'variables': variables},
        headers={
            'Content-Type': 'application/json',
            'x-hasura-admin-secret': HASURA_ADMIN_SECRET
        }
    )
    response_json = response.json()
    if 'errors' in response_json:
        app.logger.error(f"GraphQL Error: {response_json['errors']}")
        raise ValueError(f"GraphQL Error: {response_json['errors']}")
    return response_json

@app.route('/stock-price', methods=['GET'])
def stock_price_endpoint():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    price = get_stock_price(symbol)
    return jsonify({"price": price})

@app.route('/trade', methods=['POST'])
def trade_endpoint():
    data = request.get_json()
    symbol = data.get('symbol')
    volume = data.get('volume')
    trade_type = data.get('trade_type')

    if not symbol or not volume or not trade_type:
        return jsonify({"error": "Symbol, volume, and trade type are required"}), 400

    price = get_stock_price(symbol)
    stock_overview = fetch_yfinance_overview(symbol)

    check_stock_query = 'query ($ticker: String!) { stocks(where: {ticker: {_eq: $ticker}}) { ticker name } }'
    stock_response = execute_graphql(check_stock_query, variables={"ticker": symbol})
    stock_exists = stock_response['data']['stocks']

    update_stock_query = """
    mutation ($ticker: String!, $name: String!) {
        insert_stocks_one(object: { ticker: $ticker, name: $name }) {
            ticker
            name
        }
    }
    """

    update_company_overview_query = """
    mutation (
        $ticker: String!, 
        $sector: String, 
        $industry: String, 
        $marketCap: String, 
        $description: String, 
        $asOfDate: date
    ) {
        insert_company_overviews_one(object: { 
            ticker: $ticker, 
            sector: $sector, 
            industry: $industry, 
            market_cap: $marketCap, 
            description: $description, 
            as_of_date: $asOfDate 
        }) {
            ticker
            sector
        }
    }
    """

    update_portfolio_transaction_query = """
    mutation (
        $ticker: String!, 
        $transactionDate: timestamp, 
        $action: String!, 
        $volume: bigint, 
        $close: float8, 
        $totalTransactionAmount: float8
    ) {
        insert_portfolio_transactions_one(object: { 
            ticker: $ticker, 
            transaction_date: $transactionDate, 
            action: $action, 
            volume: $volume, 
            close: $close, 
            total_transaction_amount: $totalTransactionAmount 
        }) {
            ticker
            transaction_date
        }
    }
    """

    transaction_data = {
        "ticker": symbol,
        "transactionDate": datetime.utcnow().isoformat(),
        "action": trade_type,
        "volume": int(volume),  # Ensure volume is being passed as an integer
        "close": float(price),  # Ensure close price is being passed as a float
        "totalTransactionAmount": float(price * volume)  # Ensure totalTransactionAmount is being passed as a float
    }

    if not stock_exists:
        execute_graphql(update_stock_query, variables={"ticker": stock_overview["ticker"], "name": stock_overview["name"]})
        execute_graphql(update_company_overview_query, variables=stock_overview)
    
    response = execute_graphql(update_portfolio_transaction_query, variables=transaction_data)
    if 'errors' in response:
        return jsonify({"error": "Error updating portfolio transactions table", "details": response['errors']}), 500

    return jsonify({"message": "Trade executed successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)