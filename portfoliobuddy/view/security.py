from portfoliobuddy.configs import INDEX_MONKEY_PATH
import sys
from portfoliobuddy.controller.security import is_valid_yf_security, save_vol_histogram_chart
import yfinance as yf
from jinja2 import Template
from tabulate import tabulate
from telegram import MessageEntity

from portfoliobuddy.controller.portfolio_stats import can_sell_trades, asset_conc, get_position_size_and_vol_in_name, \
    get_close_value
from portfoliobuddy.view.templates.portfolio_stats import ASSET_CONCENTRATION_TEMPLATE, CAN_SELL_TEMPLATE, \
    RETURNS_TEMPLATE, VAL_TEMPLATE
from portfoliobuddy.view.utils import determine_code_entity_location, parse_pct_input


def vol_histogram(update, context):
    ticker = context.args[0].strip() if context.args else ''
    if ticker and is_valid_yf_security(ticker):
        chart_path = save_vol_histogram_chart(ticker)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart_path)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please enter a valid Yahoo! Finance ticker')
