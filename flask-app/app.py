from flask import Flask, request, jsonify
from datetime import datetime
import yfinance as yf
import requests
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import date
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
from flask_sqlalchemy import SQLAlchemy
from anthropic import Anthropic
import re

load_dotenv()

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://godzilla:Mrawww@postgres:5432/monsterverse'
db = SQLAlchemy(app)

class News(db.Model):
    __tablename__ = 'news'
    ticker = db.Column(db.String(10), primary_key=True, nullable=False)
    news = db.Column(db.String, nullable=False)
    as_of_date = db.Column(db.Date, primary_key=True, nullable=False)

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

def get_intraday_price(symbol, interval='1m'):
    try:
        ticker = yf.Ticker(symbol)
        intraday_data = ticker.history(period="1d", interval=interval)
        if not intraday_data.empty:
            price = intraday_data['Close'].iloc[-1]
        else:
            price = "N/A"
    except Exception as e:
        app.logger.error(f"Error fetching intraday stock price: {e}")
        price = "N/A"

    return price

def get_stock_tickers():
    query = """
    query {
        stocks {
            ticker
        }
    }
    """
    response = execute_graphql(query)
    tickers = [item['ticker'] for item in response['data']['stocks']]
    return tickers

def get_news(stock_list):
    print("get_news function called") 
    news_dict = {}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    if not os.path.exists('news'):
        os.makedirs('news')

    for stock in tqdm(stock_list, desc="Fetching news", unit="stock"):
        news_file_path = f"news/{stock}_news_{date.today()}.json"
        if not os.path.exists(news_file_path):
            print(f"Fetching news for: {stock}")  # Print statement to check which stock it's processing
            ticker = yf.Ticker(stock)
            news_data = ticker.news
            news_list = []

            if news_data:
                for news_item in news_data:
                    headline = news_item.get('title')
                    link = news_item.get('link')

                    if link and link.startswith('https://finance.yahoo.com'):
                        response = requests.get(link, headers=headers)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        content_div = soup.find('div', class_='caas-body')

                        if content_div:
                            for ul in content_div.find_all('ul', class_='caas-list caas-list-bullet'):
                                ul.extract()
                            content = content_div.get_text()
                        else:
                            content = "Content not found"
                    else:
                        content = "Link does not match the specified pattern"
                    
                    news_list.append({"Headline": headline, "Content": content})
                
                news_dict[stock] = news_list
                with open(news_file_path, "w") as f:
                    json.dump(news_dict[stock], f, indent=4)
            else:
                print(f"No news data retrieved for: {stock}")  # Print statement to check if no news data was retrieved
        else:
            print(f"News data for {stock} already exists for today.")  # Print statement to indicate news data already exists
      
def insert_news_to_db():
    news_dir = 'news'
    for file_name in os.listdir(news_dir):
        if file_name.endswith('.json'):
            ticker = file_name.split('_')[0]
            as_of_date_str = file_name.split('_')[2].replace('.json', '')
            as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
            
            with open(os.path.join(news_dir, file_name)) as f:
                news_data = json.load(f)
                news_text = ' '.join([item['Content'] for item in news_data])
            
                news_entry = News.query.filter_by(ticker=ticker, as_of_date=as_of_date).first()
                if not news_entry:
                    new_entry = News(ticker=ticker, news=news_text, as_of_date=as_of_date)
                    db.session.add(new_entry)
                    db.session.commit()

@app.route('/populate_db', methods=['GET'])
def populate_db():
    insert_news_to_db()
    return jsonify({"message": "Database populated successfully"}), 200

@app.route('/intraday-price', methods=['GET'])
def intraday_price_endpoint():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', '1m')  # Get the interval parameter with a default value of '1m'
    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    price = get_intraday_price(symbol, interval)
    return jsonify({"price": price})

@app.route('/stock-price', methods=['GET'])
def stock_price_endpoint():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    price = get_stock_price(symbol)
    return jsonify({"price": price})

@app.route('/get-news', methods=['GET'])
def get_news_endpoint():
    stock_list = get_stock_tickers()
    get_news(stock_list)
    return jsonify({"message": "News fetching initiated"}), 200

@app.route('/ask_warren', methods=['POST'])
def ask_warren():
    user_question = request.json.get('userQuestion')
    ticker_match = re.search(r'\$(\w+)', user_question)
    if ticker_match:
        ticker = ticker_match.group(1)
    else:
        return jsonify({"error": "No ticker symbol found in the question"}), 400

    # Extract news for the ticker
    ticker_news = ""
    news_dir = 'news'
    for file_name in os.listdir(news_dir):
        if file_name.startswith(f"{ticker}_news_"):
            with open(os.path.join(news_dir, file_name)) as f:
                news_data = json.load(f)
                for news_item in news_data:
                    ticker_news += news_item['Content'] + " "

    # Create prompt template
    with open('prompts/base_prompt.txt', 'r') as file:
        base_prompt = file.read().format(ticker=ticker, ticker_news=ticker_news, user_question=user_question)

    # Interact with Anthropic API
    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[
            {"role": "user", "content": base_prompt},
            {"role": "assistant", "content": ""}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    
    # Updated response content extraction
    if response:
        response_content = response.content[0].text.strip()
    else:
        response_content = "No response from Warren."
    print("\nResponse:\n", response, "\n Response Content:\n", response_content, "\n")
    return jsonify({"response": response_content})

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
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)