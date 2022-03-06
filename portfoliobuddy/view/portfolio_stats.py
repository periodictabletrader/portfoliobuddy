import yfinance as yf
from jinja2 import Template
from tabulate import tabulate
from telegram import MessageEntity

from portfoliobuddy.controller.portfolio_stats import can_sell_trades, asset_conc, get_position_size_and_vol_in_name
from portfoliobuddy.view.templates.portfolio_stats import ASSET_CONCENTRATION_TEMPLATE, CAN_SELL_TEMPLATE


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
    total_pf = True if context.args else None
    liquid_only = None if total_pf else True
    last_close_df = asset_conc(liquid_only=liquid_only)
    asset_conc_str = _format_asset_concentration_output(last_close_df, liquid_only=liquid_only)
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


def _parse_pct_input(pct):
    pct = float(pct)
    if pct >= 100:
        raise ValueError('Cannot lose 100% of allocation')
    elif 1 <= pct < 100:
        parsed_pct = pct / 100
    else:
        parsed_pct = pct
    return parsed_pct


def _parse_position_sizing_args(args):
    split_args = [arg.strip() for arg in ' '.join(args).split(',')]
    if len(split_args) in (3, 4):
        if len(split_args) == 3:
            ticker, period, loss_threshold_pct = split_args
            total_pf = False
        else:
            ticker, period, loss_threshold_pct, total_pf = split_args
            total_pf = bool(total_pf)
        loss_threshold_pct = _parse_pct_input(loss_threshold_pct)
        period = int(period)
        yft = yf.Ticker(ticker)
        px_hist = yft.history(period='1d')
        if px_hist.empty:
            ticker = None
    else:
        ticker, period, loss_threshold_pct, total_pf = None, None, None, None
    liquid_only = not total_pf if total_pf is not None else total_pf
    return ticker, period, loss_threshold_pct, liquid_only


def size_position(update, context):
    ticker, period, loss_threshold_pct, liquid_only = _parse_position_sizing_args(context.args)
    code_start, code_length = None, None
    if (ticker, period, loss_threshold_pct, liquid_only) == (None, None, None, None):
        reply_txt = 'Invalid input to the /size command'
    elif ticker is None:
        reply_txt = 'Ticker has no price data on Yahoo Finance'
    else:
        # calc volatility and get portfolio value and calculate what can be lost
        position_size, vol = get_position_size_and_vol_in_name(ticker, period, loss_threshold_pct, liquid_only)
        stats_output = tabulate([['Ticker', ticker],
                                 ['Position Size', f'{position_size:,.2f}'],
                                 [f'Vol over {period} days', f'{vol:.2%}']])
        reply_txt = f'''
Stats for a position in {ticker} that won't lose more than {loss_threshold_pct:.2%} of total portfolio value

{stats_output} 
        '''.strip()
        code_start, code_length = _determine_code_entity_location(reply_txt)
    no_code_block = (code_start, code_length) == (None, None)
    msg_entity = None if no_code_block else MessageEntity('code', code_start, code_length)
    msg_entities = [msg_entity] if msg_entity else None
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_txt, entities=msg_entities)
