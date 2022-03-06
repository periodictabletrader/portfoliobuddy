import datetime
from portfoliobuddy.model import Trade, ClosedTrade, session
from portfoliobuddy.controller import get_accounts, get_trade_strs
from portfoliobuddy.controller.amount_calculator import eval_expr
from portfoliobuddy.controller.portfolio_stats import can_sell_trades, asset_conc
from portfoliobuddy.controller.dates import parse_date_str
from portfoliobuddy.controller.state import AppState
from telegram import MessageEntity
from portfoliobuddy.view.templates.portfolio_stats import ASSET_CONCENTRATION_TEMPLATE, CAN_SELL_TEMPLATE
from jinja2 import Template
from tabulate import tabulate


def _can_sell_msg_txt(can_sell_df):
    can_sell_df = can_sell_df.groupby(['can_sell', 'days_to_sell']).agg(list)
    can_sell_df = can_sell_df.reset_index()
    can_sell_df = can_sell_df.sort_values('days_to_sell', ascending=False)
    can_sell_summary = can_sell_df[['can_sell', 'days_to_sell', 'ticker']].values.tolist()
    can_sell_summary = [(can_sell_, days_to_sell, list(set(tickers))) for can_sell_, days_to_sell, tickers in can_sell_summary]
    can_sell_txt = Template(CAN_SELL_TEMPLATE).render({'can_sell_summary': can_sell_summary}).strip()
    return can_sell_txt


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
    asset_conc_str = _format_asset_concentration_output(last_close_df)
    code_start, code_length = _determine_code_entity_location(asset_conc_str)
    context.bot.send_message(chat_id=update.effective_chat.id, text=asset_conc_str,
                             entities=[MessageEntity('code', code_start, code_length)])


def asset_concentration_liquid(update, context):
    last_close_df = asset_conc(liquid_only=True)
    asset_conc_str = _format_asset_concentration_output(last_close_df)
    code_start, code_length = _determine_code_entity_location(asset_conc_str)
    context.bot.send_message(chat_id=update.effective_chat.id, text=asset_conc_str,
                             entities=[MessageEntity('code', code_start, code_length)])


def _determine_code_entity_location(asset_conc_str):
    code_start = asset_conc_str.find('\n')
    code_length = len(asset_conc_str[code_start:])
    return code_start, code_length


def _format_asset_concentration_output(conc_df, liquid_only=False):
    asset_conc_template = Template(ASSET_CONCENTRATION_TEMPLATE)
    ticker_concentrations = tabulate([(row[1]['ticker'], f"{row[1]['concentration']:.1%}") for row in conc_df.iterrows()])
    template_data = {'liquid_only': liquid_only, 'ticker_concentrations': ticker_concentrations}
    return asset_conc_template.render(template_data)
