import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import openai
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from newsapi import NewsApiClient
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import nltk


class EnhancedStockAnalyzer:
    def _init_(self, logger):
        # Initialize logging and configuration
        self.logger = logger
        self.load_api_keys()

    def load_api_keys(self):
        """Secure API key management with enhanced error handling."""
        try:
            self.NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
            self.OPENAI_KEY = os.getenv('OPENAI_API_KEY')

            if not all([self.NEWSAPI_KEY, self.OPENAI_KEY]):
                raise ValueError("Missing API keys")
        except Exception as e:
            self.logger.error(f"API Key Configuration Error: {e}")
            st.error(
                "Critical configuration error. Please check your environment setup.")

    def portfolio_simulation(self, stocks, initial_investment, investment_strategy='equal_weight'):
        """
        Advanced portfolio simulation with multiple strategies

        Args:
            stocks (list): List of stock symbols
            initial_investment (float): Total investment amount
            investment_strategy (str): Strategy for allocating investments

        Returns:
            dict: Simulation results with performance metrics
        """
        try:
            # Fetch historical data for all stocks
            portfolio_data = {stock: yf.download(stock, period='1y')[
                'Adj Close'] for stock in stocks}
            self.logger.info(
                "Fetched historical data for portfolio simulation.")

            # Different allocation strategies
            if investment_strategy == 'equal_weight':
                weights = np.ones(len(stocks)) / len(stocks)
            elif investment_strategy == 'market_cap_weighted':
                # Hypothetical market cap weighting
                market_caps = [yf.Ticker(stock).info.get(
                    'marketCap', 1) for stock in stocks]
                weights = np.array(market_caps) / sum(market_caps)
            else:
                # Default to equal weight
                weights = np.ones(len(stocks)) / len(stocks)

            self.logger.info(
                f"Using investment strategy: {investment_strategy}")

            # Calculate portfolio returns
            portfolio_returns = pd.DataFrame({
                stock: data.pct_change() for stock, data in portfolio_data.items()
            })

            # Weighted portfolio returns
            weighted_returns = portfolio_returns * weights
            cumulative_portfolio_return = (1 + weighted_returns).cumprod()

            # Risk metrics
            portfolio_volatility = weighted_returns.std().sum() * np.sqrt(252)  # Annualized
            sharpe_ratio = weighted_returns.mean().sum(
            ) / portfolio_volatility if portfolio_volatility != 0 else 0

            self.logger.info("Completed portfolio simulation calculations.")

            return {
                'cumulative_returns': cumulative_portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio
            }

        except Exception as e:
            self.logger.error(f"Portfolio Simulation Error: {e}")
            st.error(f"Error during portfolio simulation: {e}")
            return None

    def advanced_correlation_analysis(self, stocks):
        """
        Create a comprehensive correlation analysis and visualization

        Args:
            stocks (list): List of stock symbols to analyze

        Returns:
            pd.DataFrame: Correlation matrix
        """
        try:
            # Fetch adjusted close prices
            data = {stock: yf.download(stock, period='1y')[
                'Adj Close'] for stock in stocks}
            returns_df = pd.DataFrame(
                {stock: df.pct_change() for stock, df in data.items()})

            # Correlation matrix
            correlation_matrix = returns_df.corr()

            self.logger.info("Computed correlation matrix.")

            # Interactive heatmap
            fig = px.imshow(
                correlation_matrix,
                labels=dict(color="Correlation"),
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                title="Stock Returns Correlation Heatmap",
                color_continuous_scale='RdBu',
                zmin=-1,
                zmax=1
            )
            st.plotly_chart(fig)
            self.logger.info("Displayed correlation heatmap.")

            return correlation_matrix

        except Exception as e:
            self.logger.error(f"Correlation Analysis Error: {e}")
            st.error(f"Error during correlation analysis: {e}")
            return None

    def machine_learning_prediction(self, stock, features=['Close', 'Volume', 'Open', 'High', 'Low']):
        """
        Advanced machine learning price prediction using Random Forest

        Args:
            stock (str): Stock symbol
            features (list): Features to use for prediction

        Returns:
            dict: Prediction results and model performance
        """
        try:
            # Fetch historical data
            data = yf.download(stock, period='5y')
            self.logger.info(
                f"Fetched historical data for ML prediction: {stock}")

            # Prepare features and target
            X = data[features]
            y = data['Close'].shift(-1)  # Next day's closing price

            # Remove NaN values
            X = X.dropna()
            y = y.dropna()

            # Align X and y
            X = X.loc[y.index]

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False)

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train Random Forest model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_train_scaled, y_train)
            self.logger.info("Trained Random Forest model for ML prediction.")

            # Predictions and evaluation
            predictions = rf_model.predict(X_test_scaled)
            mse = np.mean((predictions - y_test) ** 2)

            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': features,
                'importance': rf_model.feature_importances_
            }).sort_values('importance', ascending=False)

            self.logger.info("Completed ML prediction and evaluation.")

            return {
                'predictions': predictions,
                'mse': mse,
                'feature_importance': feature_importance
            }

        except Exception as e:
            self.logger.error(f"ML Prediction Error: {e}")
            st.error(f"Error during machine learning prediction: {e}")
            return None

    def esg_scoring(self, stock):
        """
        Retrieve and analyze ESG (Environmental, Social, Governance) metrics

        Args:
            stock (str): Stock symbol

        Returns:
            dict: ESG performance metrics
        """
        try:
            # Note: In a real implementation, you would integrate with an ESG data provider
            # This is a simulated example
            ticker = yf.Ticker(stock)
            esg_scores = {
                'Environmental Score': np.random.uniform(0, 100),
                'Social Score': np.random.uniform(0, 100),
                'Governance Score': np.random.uniform(0, 100)
            }

            # Visualize ESG scores
            fig = go.Figure(data=[
                go.Bar(
                    x=list(esg_scores.keys()),
                    y=list(esg_scores.values()),
                    marker_color=['green', 'blue', 'purple']
                )
            ])
            fig.update_layout(
                title=f'{stock} ESG Performance', yaxis_title='Score')
            st.plotly_chart(fig)
            self.logger.info(f"Displayed ESG scores for {stock}.")

            return esg_scores

        except Exception as e:
            self.logger.error(f"ESG Scoring Error: {e}")
            st.error(f"Error during ESG scoring: {e}")
            return None

# --- Logging Configuration ---


def setup_logging():
    """Set up logging with a rotating file handler and console output."""
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_filename = datetime.now().strftime("logs/app_log_%Y-%m-%d.log")
    logger = logging.getLogger(_name_)
    logger.setLevel(logging.INFO)

    # Create rotating file handler
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=5*1024*1024, backupCount=5)  # 5 MB per file, 5 backups
    # Create console handler
    stream_handler = logging.StreamHandler()

    # Define log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


logger = setup_logging()
logger.info("Application started.")

# --- Load NLTK Data ---
try:
    nltk.download('vader_lexicon')
    logger.info("NLTK 'vader_lexicon' downloaded successfully.")
except Exception as e:
    logger.exception("Error downloading NLTK data.")
    st.error(f"Error downloading NLTK data: {e}")

# --- Load Environment Variables ---
# Load environment variables from .env file if present
load_dotenv()

# --- Get API Keys from Environment Variables ---
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Validate API Keys ---
if not NEWSAPI_KEY:
    st.error("NewsAPI Key not found. Please set it in the .env file.")
    logger.error("NewsAPI Key not found in environment variables.")
    st.stop()

if not OPENAI_API_KEY:
    st.error("OpenAI API Key not found. Please set it in the .env file.")
    logger.error("OpenAI API Key not found in environment variables.")
    st.stop()

logger.info("API keys successfully loaded.")

# --- Initialize API Clients ---
try:
    newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
    openai.api_key = OPENAI_API_KEY
    logger.info("API clients initialized successfully.")
except Exception as e:
    logger.exception("Error initializing API clients.")
    st.error(f"Error initializing API clients: {e}")
    st.stop()

# --- Initialize EnhancedStockAnalyzer ---
analyzer = EnhancedStockAnalyzer(logger=logger)

# --- Streamlit App Configuration ---
st.set_page_config(
    layout="wide", page_title="Advanced Stock Analysis Dashboard")

# --- Custom CSS ---
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize session state variables for persistence ---
session_state_keys = {
    'submitted': False,
    'stock_symbol': None,
    'stock_data': None,
    'stock_info': None,
    'tech_data': None,
    'patterns': None,
    'news_articles': None,
    'avg_sentiment': None,
    'portfolio_result': None,
    'correlation_matrix': None,
    'ml_results': None,
    'esg_results': None
}

for key, default_value in session_state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# --- App Header ---
st.title('📈 Advanced Stock Insights Dashboard')

# --- Sidebar Configuration ---
st.sidebar.header('🔍 Analysis Parameters')


@st.cache_data(show_spinner=False)
def get_stock_symbol(company_name):
    prompt = f"What is the stock ticker symbol for {company_name}? Only return the symbol and nothing else."
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial assistant that knows stock ticker symbols."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0,
        )
        symbol = response.choices[0].message.content.strip().upper()
        data = yf.download(symbol, period='1d')
        if data.empty:
            return None
        return symbol
    except openai.OpenAIError as e:
        logger.error(
            f"OpenAI API error while fetching stock symbol for '{company_name}': {e}")
        st.error(f"Error getting stock symbol: {e}")
        return None
    except Exception as e:
        logger.exception(
            f"Unexpected error while fetching stock symbol for '{company_name}': {e}")
        st.error(f"Unexpected error: {e}")
        return None


def get_user_input():
    """Retrieve user inputs from the sidebar."""
    company_input = st.sidebar.text_input(
        'Company Name or Stock Symbol', 'Apple Inc.')

    # Date range selection with preset options
    date_ranges = {
        '1 Week': 7,
        '1 Month': 30,
        '3 Months': 90,
        '6 Months': 180,
        '1 Year': 365,
        'Custom': 0
    }

    selected_range = st.sidebar.selectbox(
        'Select Time Range', list(date_ranges.keys()))

    if selected_range == 'Custom':
        start_date = st.sidebar.date_input('Start Date',
                                           datetime.today() - timedelta(days=365))
        end_date = st.sidebar.date_input('End Date', datetime.today())
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=date_ranges[selected_range])

    # Technical Analysis Parameters
    st.sidebar.subheader('Technical Indicators')
    show_sma = st.sidebar.checkbox('Show Simple Moving Averages', True)
    show_rsi = st.sidebar.checkbox('Show RSI', True)
    show_macd = st.sidebar.checkbox('Show MACD', True)
    show_bollinger = st.sidebar.checkbox('Show Bollinger Bands', True)

    # Prediction Parameters
    st.sidebar.subheader('Prediction Parameters')
    prediction_days = st.sidebar.slider(
        "Days to Predict", 1, 30, 5)

    # Enhanced Features Parameters
    st.sidebar.subheader('Enhanced Features')

    # Portfolio Simulation
    run_portfolio = st.sidebar.checkbox("Run Portfolio Simulation")
    portfolio_input = ""
    portfolio_stocks = []
    initial_investment = 0
    strategy = ''
    if run_portfolio:
        portfolio_input = st.sidebar.text_input(
            "Enter stock symbols or company names for Portfolio Simulation (separated by commas)", "AAPL, GOOGL, MSFT")
        initial_investment = st.sidebar.number_input(
            "Initial Investment",
            min_value=1000,
            value=10000
        )
        strategy = st.sidebar.selectbox(
            "Investment Strategy",
            ['Equal Weight', 'Market Cap Weighted']
        )

    # Correlation Analysis
    run_correlation = st.sidebar.checkbox("Correlation Analysis")
    correlation_input = ""
    correlation_stocks = []
    if run_correlation:
        correlation_input = st.sidebar.text_input(
            "Enter stock symbols or company names for Correlation Analysis (separated by commas)", "AAPL, GOOGL, MSFT")

    # Machine Learning Prediction
    run_ml = st.sidebar.checkbox("ML Price Prediction")
    ml_input = ""
    ml_stock = None
    if run_ml:
        ml_input = st.sidebar.text_input(
            "Enter stock symbol or company name for ML Prediction", "AAPL")

    # ESG Scoring
    run_esg = st.sidebar.checkbox("ESG Performance")
    esg_input = ""
    esg_stock = None
    if run_esg:
        esg_input = st.sidebar.text_input(
            "Enter stock symbol or company name for ESG Analysis", "AAPL")

    # Add a 'Submit' button
    submitted = st.sidebar.button('Submit')

    logger.info("User input retrieved from sidebar.")
    return (company_input, start_date, end_date, show_sma, show_rsi, show_macd, show_bollinger,
            prediction_days, run_portfolio, portfolio_input, initial_investment, strategy,
            run_correlation, correlation_input,
            run_ml, ml_input,
            run_esg, esg_input,
            submitted)

# --- Technical Analysis Functions ---


def calculate_technical_indicators(data):
    """Calculate comprehensive technical indicators"""
    df = data.copy()

    # Simple Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()

    # Exponential Moving Averages
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + 2 * bb_std
    df['BB_lower'] = df['BB_middle'] - 2 * bb_std

    # Volatility
    df['Volatility'] = df['Close'].rolling(window=20).std()

    # Average True Range (ATR)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()

    logger.info("Technical indicators calculated.")
    return df


def analyze_patterns(data):
    """Analyze trading patterns and signals"""
    patterns = []

    # Ensure sufficient data for analysis
    if len(data) < 50:
        logger.warning("Not enough data to analyze patterns.")
        return patterns

    # Moving Average Crossovers
    if (data['SMA_20'].iloc[-1] > data['SMA_50'].iloc[-1] and
            data['SMA_20'].iloc[-2] <= data['SMA_50'].iloc[-2]):
        patterns.append("Golden Cross detected (bullish)")
    elif (data['SMA_20'].iloc[-1] < data['SMA_50'].iloc[-1] and
          data['SMA_20'].iloc[-2] >= data['SMA_50'].iloc[-2]):
        patterns.append("Death Cross detected (bearish)")

    # RSI Signals
    current_rsi = data['RSI'].iloc[-1]
    if current_rsi > 70:
        patterns.append(f"Overbought conditions (RSI: {current_rsi:.2f})")
    elif current_rsi < 30:
        patterns.append(f"Oversold conditions (RSI: {current_rsi:.2f})")

    # MACD Signals
    if (data['MACD'].iloc[-1] > data['Signal_Line'].iloc[-1] and
            data['MACD'].iloc[-2] <= data['Signal_Line'].iloc[-2]):
        patterns.append("MACD bullish crossover")
    elif (data['MACD'].iloc[-1] < data['Signal_Line'].iloc[-1] and
          data['MACD'].iloc[-2] >= data['Signal_Line'].iloc[-2]):
        patterns.append("MACD bearish crossover")

    # Bollinger Band Signals
    last_close = data['Close'].iloc[-1]
    if last_close > data['BB_upper'].iloc[-1]:
        patterns.append(
            "Price above upper Bollinger Band (potential reversal)")
    elif last_close < data['BB_lower'].iloc[-1]:
        patterns.append(
            "Price below lower Bollinger Band (potential reversal)")

    logger.info(f"Patterns analyzed: {patterns}")
    return patterns

# --- Data Loading Functions ---


@st.cache_data(show_spinner=False)
def load_stock_data(symbol, start, end):
    try:
        logger.info(
            f"Fetching stock data for symbol '{symbol}' from {start} to {end}.")
        data = yf.download(symbol, start=start, end=end)
        if data.empty:
            logger.warning(
                f"No data found for symbol '{symbol}' in the specified date range.")
            return None
        data.reset_index(inplace=True)
        logger.info(f"Successfully fetched stock data for '{symbol}'.")
        return data
    except Exception as e:
        logger.exception(f"Error fetching data for '{symbol}': {e}")
        st.error(f"Error fetching data for {symbol}: {e}")
        return None


@st.cache_data(show_spinner=False)
def load_stock_info(symbol):
    try:
        logger.info(f"Fetching stock info for symbol '{symbol}'.")
        stock = yf.Ticker(symbol)
        info = stock.info
        logger.info(f"Successfully fetched stock info for '{symbol}'.")
        return info
    except Exception as e:
        logger.exception(f"Error fetching stock info for '{symbol}': {e}")
        st.error(f"Error fetching stock info: {e}")
        return None

# --- Sentiment Analysis Function ---


def analyze_sentiment(articles):
    """Perform sentiment analysis on news articles."""
    sia = SentimentIntensityAnalyzer()
    sentiments = []

    for article in articles:
        text = article.get('description') or article.get('content') or ''
        if text:
            sentiment = sia.polarity_scores(text)
            article['sentiment'] = sentiment
            sentiments.append(sentiment['compound'])

    # Calculate average sentiment
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
    else:
        avg_sentiment = 0

    logger.info(
        f"Sentiment analysis completed. Average sentiment: {avg_sentiment:.2f}")
    return articles, avg_sentiment

# --- News Loading Function ---


@st.cache_data(show_spinner=False)
def load_news(ticker, from_date, to_date):
    try:
        logger.info(
            f"Fetching news for '{ticker}' from {from_date} to {to_date}.")
        all_articles = newsapi.get_everything(
            q=ticker,
            from_param=from_date.strftime('%Y-%m-%d'),
            to=to_date.strftime('%Y-%m-%d'),
            language='en',
            sort_by='relevancy',
            page_size=10
        )
        logger.info(f"Successfully fetched news articles for '{ticker}'.")
        return all_articles.get('articles', [])
    except Exception as e:
        logger.exception(f"Error fetching news for '{ticker}': {e}")
        st.error(f"Error fetching news: {e}")
        return []

# --- Article Summarization Function ---


@st.cache_data(show_spinner=False)
def summarize_article(article_text):
    """Summarize a news article using OpenAI's GPT model."""
    prompt = f"Summarize the following news article in 2-3 sentences:\n\n{article_text}"

    try:
        logger.info("Requesting summary from OpenAI.")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that summarizes news articles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        logger.info("Summary generated successfully.")
        return summary
    except openai.OpenAIError as e:
        logger.error(
            f"OpenAI API error during article summarization: {e}")
        return "Summary not available."
    except Exception as e:
        logger.exception(
            f"Unexpected error during article summarization: {e}")
        return "Summary not available."

# --- AI Insights Generation Function ---


@st.cache_data(show_spinner=False)
def generate_ai_insights(symbol, data, articles, patterns, stock_info, avg_sentiment):
    """Enhanced AI insights generation with sentiment analysis"""
    logger.info(f"Generating AI insights for symbol '{symbol}'.")
    # Prepare technical analysis summary
    latest_close = data['Close'].iloc[-1]
    if len(data) >= 2:
        prev_close = data['Close'].iloc[-2]
    else:
        prev_close = latest_close  # If not enough data, use latest close
    price_change = latest_close - prev_close
    if prev_close != 0:
        price_change_pct = (price_change / prev_close) * 100
    else:
        price_change_pct = 0.0

    # Prepare market context
    market_cap = stock_info.get('marketCap', 'N/A')
    pe_ratio = stock_info.get('trailingPE', 'N/A')

    # Prepare news summary
    news_summary = "\n".join([
        f"- {article['title']}" for article in articles[:5]
    ])

    # Prepare patterns
    pattern_summary = ', '.join(
        patterns) if patterns else 'No significant patterns detected'

    # Include sentiment in the prompt
    sentiment_label = "neutral"
    if avg_sentiment > 0.05:
        sentiment_label = "positive"
    elif avg_sentiment < -0.05:
        sentiment_label = "negative"

    prompt = f"""As a senior financial analyst, provide a comprehensive analysis of {symbol}:

Technical Analysis:
- Current Price: ${latest_close:.2f} ({price_change_pct:.2f}% change)
- Market Cap: {market_cap}
- P/E Ratio: {pe_ratio}
- Recent Patterns: {pattern_summary}

News Sentiment:
- The overall news sentiment is {sentiment_label} with a sentiment score of {avg_sentiment:.2f}.

News Highlights:
{news_summary}

Based on the above data, market trends, and news sentiment, provide insights and discuss factors that could influence the future outlook for {symbol}.
"""

    try:
        logger.info("Sending prompt to OpenAI for AI insights.")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are a seasoned financial analyst providing detailed stock analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        analysis = response.choices[0].message.content.strip()
        logger.info("Successfully received AI insights from OpenAI.")
        return analysis
    except openai.OpenAIError as e:
        logger.error(
            f"OpenAI API error during AI insights generation: {e}")
        return f"AI analysis not available due to an error: {e}"
    except Exception as e:
        logger.exception(
            f"Unexpected error during AI insights generation: {e}")
        return f"AI analysis not available due to an unexpected error: {e}"

# --- Risk Assessment Function ---


@st.cache_data(show_spinner=False)
def generate_risk_assessment(symbol, data, avg_sentiment):
    """Generate a risk assessment for the stock."""
    logger.info(f"Generating risk assessment for symbol '{symbol}'.")
    volatility = data['Volatility'].iloc[-1]

    prompt = f"""As a risk analyst, assess the risk level of investing in {symbol}:

- Current Volatility: {volatility:.2f}
- News Sentiment Score: {avg_sentiment:.2f}

Consider market conditions, volatility, and news sentiment in your assessment.
"""

    try:
        logger.info("Sending risk assessment prompt to OpenAI.")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a financial risk analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        assessment = response.choices[0].message.content.strip()
        logger.info("Risk assessment received.")
        return assessment
    except openai.OpenAIError as e:
        logger.error(
            f"OpenAI API error during risk assessment generation: {e}")
        return f"Risk assessment not available due to an error: {e}"
    except Exception as e:
        logger.exception(
            f"Unexpected error during risk assessment generation: {e}")
        return f"Risk assessment not available due to an unexpected error: {e}"

# --- Helper Function to Process Multiple Inputs ---


def process_multiple_inputs(input_str):
    """
    Process a comma-separated string of company names or stock symbols.

    Args:
        input_str (str): Comma-separated company names or stock symbols.

    Returns:
        list: List of valid stock symbols.
    """
    if not input_str:
        return []

    inputs = [item.strip() for item in input_str.split(',')]
    symbols = []

    for item in inputs:
        symbol = get_stock_symbol(item)
        if symbol:
            symbols.append(symbol)
        else:
            logger.warning(f"Invalid stock symbol or company name: {item}")
            st.warning(f"Could not find a valid stock symbol for: {item}")

    return symbols

# --- Initialize session state variables for persistence ---
# (Already initialized earlier)


# --- Function to Get User Input ---
user_input_tuple = get_user_input()
(company_input, start_date, end_date, show_sma, show_rsi, show_macd, show_bollinger,
 prediction_days, run_portfolio, portfolio_input, initial_investment, strategy,
 run_correlation, correlation_input,
 run_ml, ml_input,
 run_esg, esg_input,
 submitted) = user_input_tuple

# --- Process Submission ---
if submitted:
    with st.spinner('Processing your request...'):
        # Convert main company name to stock symbol
        stock_symbol = get_stock_symbol(company_input)
        if stock_symbol is None:
            st.error(
                f"Could not find a stock symbol for '{company_input}'. Please check the company name and try again.")
            st.stop()

        st.session_state['stock_symbol'] = stock_symbol
        st.session_state['submitted'] = True

        # Load Data
        stock_data = load_stock_data(stock_symbol, start_date, end_date)
        if stock_data is None:
            st.error(
                f"No data found for {stock_symbol}. Please check the symbol and try again.")
            st.stop()

        st.session_state['stock_data'] = stock_data

        # Load Stock Info
        stock_info = load_stock_info(stock_symbol)
        st.session_state['stock_info'] = stock_info

        # Calculate Technical Indicators
        tech_data = calculate_technical_indicators(stock_data)
        st.session_state['tech_data'] = tech_data

        # Analyze Patterns
        patterns = analyze_patterns(tech_data)
        st.session_state['patterns'] = patterns

        # Fetch News Articles
        news_articles = load_news(stock_symbol, start_date, end_date)
        news_articles, avg_sentiment = analyze_sentiment(news_articles)
        st.session_state['news_articles'] = news_articles
        st.session_state['avg_sentiment'] = avg_sentiment

        # Handle Portfolio Simulation if selected
        if run_portfolio and portfolio_input:
            portfolio_stocks = process_multiple_inputs(portfolio_input)
            if portfolio_stocks:
                portfolio_result = analyzer.portfolio_simulation(
                    portfolio_stocks,
                    initial_investment,
                    strategy.lower().replace(' ', '_')
                )
                st.session_state['portfolio_result'] = portfolio_result
            else:
                st.warning(
                    "No valid stocks provided for portfolio simulation.")

        # Handle Correlation Analysis if selected
        if run_correlation and correlation_input:
            correlation_stocks = process_multiple_inputs(correlation_input)
            if correlation_stocks:
                correlation_matrix = analyzer.advanced_correlation_analysis(
                    correlation_stocks)
                st.session_state['correlation_matrix'] = correlation_matrix
            else:
                st.warning(
                    "No valid stocks provided for correlation analysis.")

        # Handle ML Prediction if selected
        if run_ml and ml_input:
            ml_stock = get_stock_symbol(ml_input)
            if ml_stock:
                ml_results = analyzer.machine_learning_prediction(ml_stock)
                st.session_state['ml_results'] = ml_results
            else:
                st.warning("Invalid stock provided for ML prediction.")

        # Handle ESG Scoring if selected
        if run_esg and esg_input:
            esg_stock = get_stock_symbol(esg_input)
            if esg_stock:
                esg_results = analyzer.esg_scoring(esg_stock)
                st.session_state['esg_results'] = esg_results
            else:
                st.warning("Invalid stock provided for ESG scoring.")

# --- Load Stored Data from Session State ---
stock_data = st.session_state['stock_data']
stock_info = st.session_state['stock_info']
stock_symbol = st.session_state['stock_symbol']
tech_data = st.session_state['tech_data']
patterns = st.session_state['patterns']
news_articles = st.session_state['news_articles']
avg_sentiment = st.session_state['avg_sentiment']
portfolio_result = st.session_state['portfolio_result']
correlation_matrix = st.session_state['correlation_matrix']
ml_results = st.session_state['ml_results']
esg_results = st.session_state['esg_results']

# --- Display Dashboard if Data is Available ---
if st.session_state['submitted'] and stock_data is not None and stock_info is not None:
    # Dashboard Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📊 {stock_symbol} Price Analysis")

        # Create interactive price chart using Plotly
        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=stock_data['Date'],
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
            name='OHLC'
        ))

        # Add technical indicators based on user selection
        if show_sma:
            fig.add_trace(go.Scatter(
                x=tech_data['Date'],
                y=tech_data['SMA_20'],
                name='SMA 20',
                line=dict(color='orange')
            ))
            fig.add_trace(go.Scatter(
                x=tech_data['Date'],
                y=tech_data['SMA_50'],
                name='SMA 50',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=tech_data['Date'],
                y=tech_data['SMA_200'],
                name='SMA 200',
                line=dict(color='green')
            ))

        if show_bollinger:
            fig.add_trace(go.Scatter(
                x=tech_data['Date'],
                y=tech_data['BB_upper'],
                name='BB Upper',
                line=dict(color='gray', dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=tech_data['Date'],
                y=tech_data['BB_lower'],
                name='BB Lower',
                line=dict(color='gray', dash='dash'),
                fill='tonexty'
            ))

        fig.update_layout(
            title=f'{stock_symbol} Price Chart',
            yaxis_title='Price (USD)',
            xaxis_title='Date',
            template='plotly_white',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
        logger.info("Price chart displayed.")

    with col2:
        st.subheader("📈 Quick Stats")

        if stock_info:
            metrics = {
                "Current Price": stock_info.get('currentPrice', 'N/A'),
                "Market Cap": f"${stock_info.get('marketCap', 0):,}",
                "P/E Ratio": stock_info.get('trailingPE', 'N/A'),
                "52W High": stock_info.get('fiftyTwoWeekHigh', 'N/A'),
                "52W Low": stock_info.get('fiftyTwoWeekLow', 'N/A'),
                "Volume": f"{stock_info.get('volume', 0):,}"
            }

            for metric, value in metrics.items():
                st.metric(metric, value)
            logger.info("Quick stats displayed.")

    # Technical Analysis Section
    st.subheader("📊 Technical Analysis")

    if show_rsi:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=tech_data['Date'],
            y=tech_data['RSI'],
            name='RSI'
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(
            title='Relative Strength Index (RSI)',
            yaxis_title='RSI Value',
            height=300
        )
        st.plotly_chart(fig_rsi, use_container_width=True)
        logger.info("RSI chart displayed.")

    if show_macd:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=tech_data['Date'],
            y=tech_data['MACD'],
            name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(
            x=tech_data['Date'],
            y=tech_data['Signal_Line'],
            name='Signal Line'
        ))
        fig_macd.add_bar(
            x=tech_data['Date'],
            y=tech_data['MACD_Histogram'],
            name='MACD Histogram'
        )
        fig_macd.update_layout(
            title='MACD Indicator',
            yaxis_title='Value',
            height=300
        )
        st.plotly_chart(fig_macd, use_container_width=True)
        logger.info("MACD chart displayed.")

    # Pattern Analysis
    st.subheader("🎯 Pattern Analysis")
    if patterns:
        for pattern in patterns:
            st.info(pattern)
    else:
        st.write("No significant patterns detected in the current timeframe.")
    logger.info("Pattern analysis displayed.")

    # News Section with Sentiment Analysis
    st.subheader("📰 Latest News & Sentiment Analysis")

    # Display average sentiment
    sentiment_label = "Neutral 😐"
    if avg_sentiment > 0.05:
        sentiment_label = "Positive 😊"
    elif avg_sentiment < -0.05:
        sentiment_label = "Negative 😞"

    st.write(
        f"*Overall News Sentiment:* {sentiment_label} (Score: {avg_sentiment:.2f})")

    if news_articles:
        for article in news_articles:
            sentiment = article.get('sentiment', {})
            sentiment_score = sentiment.get('compound', 0)
            sentiment_text = "Neutral 😐"

            if sentiment_score > 0.05:
                sentiment_text = "Positive 😊"
            elif sentiment_score < -0.05:
                sentiment_text = "Negative 😞"

            article_text = article.get(
                'description') or article.get('content') or ''
            summary = article_text  # Default summary is the description

            with st.expander(f"{article['title']}"):
                st.write(
                    f"*Sentiment:* {sentiment_text} (Score: {sentiment_score:.2f})")
                st.write(
                    f"*Source:* {article['source']['name']}  |  *Published At:* {article['publishedAt']}")

                if st.button('Summarize Article', key=article['url']):
                    with st.spinner('Summarizing article...'):
                        summary = summarize_article(article_text)
                        st.write(f"*Summary:* {summary}")
                else:
                    st.write(f"*Summary:* {summary}")
                st.write(f"[Read more...]({article['url']})")
        logger.info("News articles displayed.")
    else:
        st.write('No news articles found for this date range.')
        logger.info("No news articles found.")

    # AI Insights Generation
    st.subheader("🤖 AI-Powered Analysis and Outlook")

    with st.spinner('Generating AI insights...'):
        ai_insights = generate_ai_insights(
            stock_symbol, tech_data, news_articles, patterns, stock_info, avg_sentiment
        )
        st.write(ai_insights)
        logger.info("AI insights displayed.")

    # Prediction Logic using Prophet
    st.header("📈 Stock Price Prediction with Prophet")

    if st.button("Predict Future Prices"):
        # Prepare the data for Prophet
        df_prophet = stock_data[['Date', 'Close']].rename(
            columns={'Date': 'ds', 'Close': 'y'})
        df_prophet = df_prophet.dropna()

        # Fit the Prophet model
        with st.spinner('Training Prophet model...'):
            try:
                model = Prophet(daily_seasonality=True)
                model.fit(df_prophet)
                logger.info("Prophet model trained successfully.")
            except Exception as e:
                logger.exception(f"Error training Prophet model: {e}")
                st.error(f"Error training Prophet model: {e}")
                st.stop()

        # Create a dataframe to hold predictions
        future = model.make_future_dataframe(periods=prediction_days)

        # Forecast
        with st.spinner('Forecasting future prices...'):
            try:
                forecast = model.predict(future)
                logger.info("Forecast generated successfully.")
            except Exception as e:
                logger.exception(f"Error during forecasting: {e}")
                st.error(f"Error during forecasting: {e}")
                st.stop()

        # Plot the forecast
        fig_forecast = go.Figure()

        # Historical Close
        fig_forecast.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            name='Close Price',
            line=dict(color='blue')
        ))

        # Forecasted Close
        fig_forecast.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            name='Upper Confidence',
            line=dict(color='lightblue'),
            showlegend=False
        ))
        fig_forecast.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            name='Lower Confidence',
            line=dict(color='lightblue'),
            fill='tonexty',
            fillcolor='rgba(173,216,230,0.2)',
            showlegend=False
        ))

        fig_forecast.update_layout(
            title=f'{stock_symbol} Price Prediction for Next {prediction_days} Days',
            yaxis_title='Price (USD)',
            xaxis_title='Date',
            template='plotly_white',
            height=600
        )

        # Display the forecast
        st.plotly_chart(fig_forecast, use_container_width=True)

        # Show forecast data
        st.write("📅 *Forecasted Prices*")
        forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(
            prediction_days)
        forecast_display = forecast_display.rename(columns={
            'ds': 'Date',
            'yhat': 'Predicted Close',
            'yhat_lower': 'Lower Confidence',
            'yhat_upper': 'Upper Confidence'
        })
        st.dataframe(forecast_display)
        logger.info("Forecasted prices displayed.")

    # User Queries and Q&A Section
    st.subheader("💬 Ask a Question about the Stock")

    user_question = st.text_input("Enter your question:")
    if st.button('Get Answer'):
        if user_question:
            prompt = f"""You are a financial assistant. Based on the available data and news, answer the following question:

Question: {user_question}

Provide a concise and informative answer.
"""

            with st.spinner('Generating answer...'):
                try:
                    logger.info("Sending user question to OpenAI.")
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system",
                             "content": "You are a helpful financial assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.7,
                    )
                    answer = response.choices[0].message.content.strip()
                    st.write(answer)
                    logger.info("Answer received and displayed.")
                except openai.OpenAIError as e:
                    logger.error(f"Error generating answer: {e}")
                    st.error(f"Error generating answer: {e}")
        else:
            st.write("Please enter a question and click 'Get Answer'.")
    else:
        st.write("Please enter a question and click 'Get Answer'.")

    # Risk Assessment Analysis
    st.subheader("⚠ Risk Assessment")

    with st.spinner('Generating risk assessment...'):
        risk_assessment = generate_risk_assessment(
            stock_symbol, tech_data, avg_sentiment)
        st.write(risk_assessment)
        logger.info("Risk assessment displayed.")

    # --- Enhanced Features Integration ---

    # Portfolio Simulation
    if run_portfolio and portfolio_result:
        st.header("📈 Portfolio Tracking and Simulation")
        st.subheader("📊 Portfolio Performance")

        # Plot cumulative returns
        fig_portfolio = go.Figure()
        for stock in portfolio_result['cumulative_returns']:
            fig_portfolio.add_trace(go.Scatter(
                x=portfolio_result['cumulative_returns'].index,
                y=portfolio_result['cumulative_returns'][stock],
                mode='lines',
                name=stock
            ))

        fig_portfolio.update_layout(
            title='Cumulative Portfolio Returns',
            xaxis_title='Date',
            yaxis_title='Cumulative Returns',
            template='plotly_white',
            height=600
        )
        st.plotly_chart(fig_portfolio, use_container_width=True)

        # Display risk metrics
        st.subheader("📊 Portfolio Risk Metrics")
        st.write(f"*Volatility:* {portfolio_result['volatility']:.2%}")
        st.write(
            f"*Sharpe Ratio:* {portfolio_result['sharpe_ratio']:.2f}")

    # Correlation Analysis
    if run_correlation and correlation_matrix is not None:
        st.header("📊 Advanced Correlation Analysis")
        st.write("*Correlation Matrix:*")
        fig_corr = px.imshow(
            correlation_matrix,
            labels=dict(color="Correlation"),
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            title="Stock Returns Correlation Heatmap",
            color_continuous_scale='RdBu',
            zmin=-1,
            zmax=1
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # Machine Learning Prediction
    if run_ml and ml_results:
        if len(ml_results['predictions']) != len(stock_data['Date'][-len(ml_results['predictions']):]):
            st.error(
                "Prediction data length does not match the available test data. Ensure proper alignment.")
        else:
            st.header("🤖 Machine Learning Price Prediction")
            st.subheader("📈 Prediction Results")
            prediction_dates = stock_data['Date'][-len(
                ml_results['predictions']):]
            prediction_df = pd.DataFrame({
                'Date': prediction_dates,
                'Predicted Close': ml_results['predictions']
            })

            fig_ml_pred = go.Figure()
            fig_ml_pred.add_trace(go.Scatter(
                x=prediction_df['Date'],
                y=prediction_df['Predicted Close'],
                mode='lines',
                name='Predicted Close'
            ))
            fig_ml_pred.update_layout(
                title=f'{ml_stock} Predicted Close Prices',
                xaxis_title='Date',
                yaxis_title='Predicted Close Price (USD)',
                template='plotly_white',
                height=600
            )
            st.plotly_chart(fig_ml_pred, use_container_width=True)

            st.subheader("📊 Model Performance")
            st.write(f"*Mean Squared Error (MSE):* {ml_results['mse']:.4f}")

            st.subheader("🔍 Feature Importance")
            feature_importance = ml_results['feature_importance']
            fig_feat_imp = px.bar(feature_importance, x='feature', y='importance',
                                  title='Feature Importance',
                                  labels={'importance': 'Importance', 'feature': 'Feature'})
            st.plotly_chart(fig_feat_imp, use_container_width=True)

    # ESG Scoring
    if run_esg and esg_results:
        st.header("🌱 Sustainability and ESG Scoring")
        st.subheader(f"{esg_stock} ESG Performance")
        esg_scores = esg_results
        fig_esg = go.Figure(data=[
            go.Bar(
                x=list(esg_scores.keys()),
                y=list(esg_scores.values()),
                marker_color=['green', 'blue', 'purple']
            )
        ])
        fig_esg.update_layout(
            title=f'{esg_stock} ESG Performance',
            yaxis_title='Score',
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig_esg, use_container_width=True)

# If not submitted, display a welcome message
else:
    st.write("Please enter the analysis parameters and click Submit.")
