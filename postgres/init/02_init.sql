-- Create stocks table
CREATE TABLE IF NOT EXISTS stocks (
    ticker VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255)
);

-- Create portfolio table
CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) REFERENCES stocks(ticker),
    transaction_date DATE,
    action VARCHAR(50),
    volume INT,
    time TIME,
    close FLOAT,
    total_transaction_amount FLOAT
);

-- Create company_overview table
CREATE TABLE IF NOT EXISTS company_overview (
    ticker VARCHAR(50) PRIMARY KEY REFERENCES stocks(ticker),
    sector VARCHAR(255),
    industry VARCHAR(255),
    market_cap VARCHAR(255),
    description TEXT,
    as_of_date DATE
);

-- Create earnings table
CREATE TABLE IF NOT EXISTS earnings (
    earnings_id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) REFERENCES stocks(ticker),
    fiscal_year INT,
    fiscal_period VARCHAR(50),
    eps FLOAT,
    as_of_date DATE
);

-- Create ticker_daily table
CREATE TABLE IF NOT EXISTS ticker_daily (
    daily_price_id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) REFERENCES stocks(ticker),
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT
);

-- Create ticker_intraday table
CREATE TABLE IF NOT EXISTS ticker_intraday (
    intraday_price_id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) REFERENCES stocks(ticker),
    date_time TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO godzilla;
