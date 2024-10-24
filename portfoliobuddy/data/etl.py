import pandas as pd
import datetime
import yfinance as yf
from pandas.tseries.offsets import BDay
import sqlite3
from portfoliobuddy.constants import DB_NAME, PF_SHEET


def read_portfolio():
    portfolio = pd.read_csv(
        PF_SHEET,
        dtype={
            'FX': 'float64',
            'Qty': 'float64',
            'Value at Buy (GBP)': 'float64',
            'Value Today (ccy)': 'float64',
            'Value Today (GBP)': 'float64',
            'Gain/Loss': 'float64',
            # 'Gain/Loss (%)': 'float64',
        }
    )
    return portfolio


def prep_portfolio(run_date=None):
    pf = read_portfolio()
    run_date = run_date or datetime.date.today()
    eod = datetime.datetime(run_date.year, run_date.month, run_date.day) - BDay(1)
    prepped_pf = pf[['Yfinance Ticker', 'Time Horizon', 'Idea', 'Account', 'Qty', 'FX', 'Value at Buy (GBP)', 'Value Today (GBP)']]
    prepped_pf = prepped_pf.rename(columns={
        'Yfinance Ticker': 'ticker',
        'Time Horizon': 'horizon',
        'Idea': 'idea',
        'Account': 'account',
        'Qty': 'qty',
        'Value at Buy (GBP)': 'buyval',
        'Value Today (GBP)': 'mtmval_fallback',
    })
    prepped_pf = prepped_pf[~prepped_pf['ticker'].isna()]
    prepped_pf['posdate'] = eod
    tickers = prepped_pf['ticker'].to_list()
    yf_tickers = yf.Tickers(tickers)
    px = yf_tickers.history('5d')['Close']
    px = px.loc[eod.strftime('%Y-%m-%d')]
    ticker_px = px.transpose().reset_index()
    ticker_px.columns = ['ticker', 'px']
    prepped_pf = pd.merge(prepped_pf, ticker_px, left_on='ticker', right_on='ticker', how='left')
    prepped_pf['mtmval'] = prepped_pf['qty'] * prepped_pf['px'] * prepped_pf['FX']
    prepped_pf.loc[prepped_pf['mtmval'].isna(), 'mtmval'] = prepped_pf['mtmval_fallback']
    prepped_pf = prepped_pf[['posdate', 'ticker', 'horizon', 'idea', 'account', 'qty', 'buyval', 'mtmval']]
    return prepped_pf


def upload_portfolio(run_date=None):
    portfolio = prep_portfolio(run_date)
    conn = sqlite3.connect(DB_NAME)
    portfolio.to_sql('positions', conn, if_exists='append', index=False)
    conn.close()


if __name__ == '__main__':
    upload_portfolio()
