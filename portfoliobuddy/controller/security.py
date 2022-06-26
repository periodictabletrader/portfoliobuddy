import datetime
import yfinance as yf
from matplotlib import pyplot as plt
from portfoliobuddy.configs import INDEX_MONKEY_PATH, CHART_STORAGE_LOCATION
import sys
sys.path.append(INDEX_MONKEY_PATH)
from index_monkey.analysis.volatility.charts import chart_volatility_histogram


def is_valid_yf_security(ticker):
    yf_ticker = yf.Ticker(ticker)
    px = yf_ticker.history('1D')
    is_valid = not px.empty
    return is_valid


def save_vol_histogram_chart(ticker):
    chart_file_name = f'{CHART_STORAGE_LOCATION}/{datetime.date.today()}_{ticker}_vol_histogram.png'
    chart_volatility_histogram(ticker)
    plt.savefig(chart_file_name, transparent=False, facecolor='white', bbox_inches='tight')
    return chart_file_name
