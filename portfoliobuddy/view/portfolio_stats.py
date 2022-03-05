import datetime
from portfoliobuddy.model import Trade, ClosedTrade, session
from portfoliobuddy.controller import get_accounts, get_trade_strs
from portfoliobuddy.controller.amount_calculator import eval_expr
from portfoliobuddy.controller.portfolio_stats import can_sell_trades, asset_conc
from portfoliobuddy.controller.dates import parse_date_str
from portfoliobuddy.controller.state import AppState
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from portfoliobuddy.view.templates.portfolio_stats import ASSET_CONCENTRATION_TEMPLATE
from jinja2 import Template


def _can_sell_msg_txt(can_sell_df):
    can_sell_df = can_sell_df[['account', 'can_sell', 'ticker']]
    can_sell_df = can_sell_df.groupby(['account', 'can_sell']).agg(list)
    can_sell_df = can_sell_df.sort_values('can_sell')
    msg_txt = ''
    for acc, can_sell_, tickers in can_sell_df.iterrows():
        if can_sell_:
            line = f'{", ".join(tickers)} in {acc} can be sold'
        else:
            line = f'{", ".join(tickers)} in {acc} cannot be sold'
        msg_txt = f'{msg_txt}\n{line}'
    msg_txt = msg_txt.strip()
    return msg_txt


def can_sell(update, context):
    args = context.args
    tickers = None
    if args:
        tickers = [ticker.strip() for ticker in args.split(',')]
    can_sell_trades_df = can_sell_trades(tickers)
    can_sell_response = _can_sell_msg_txt(can_sell_trades_df)
    context.bot.send_message(chat_id=update.effective_chat.id, text=can_sell_response)


def asset_concentration(update, context):
    last_close_df = asset_conc()
    context.bot.send_message(chat_id=update.effective_chat.id, text=_format_asset_concentration_output(last_close_df))


def asset_concentration_liquid(update, context):
    last_close_df = asset_conc(liquid_only=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=_format_asset_concentration_output(last_close_df))


def _format_asset_concentration_output(conc_df, liquid_only=False):
    asset_conc_template = Template(ASSET_CONCENTRATION_TEMPLATE)
    ticker_concentrations = [(row[1]['ticker'], row[1]['concentration']) for row in conc_df.iterrows()]
    template_data = {'liquid_only': liquid_only, 'ticker_concentrations': ticker_concentrations}
    return asset_conc_template.render(template_data)
