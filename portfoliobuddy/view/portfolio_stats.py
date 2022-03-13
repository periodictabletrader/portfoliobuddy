import yfinance as yf
from jinja2 import Template
from tabulate import tabulate
from telegram import MessageEntity

from portfoliobuddy.controller.portfolio_stats import can_sell_trades, asset_conc, get_position_size_and_vol_in_name, \
    get_close_value
from portfoliobuddy.view.templates.portfolio_stats import ASSET_CONCENTRATION_TEMPLATE, CAN_SELL_TEMPLATE, \
    RETURNS_TEMPLATE
from portfoliobuddy.view.utils import determine_code_entity_location, parse_pct_input


# region can_sell
def can_sell(update, context):
    args = context.args
    tickers = None
    if args:
        tickers = [ticker.strip() for ticker in args.split(',')]
    can_sell_trades_df = can_sell_trades(tickers)
    can_sell_response = _can_sell_msg_txt(can_sell_trades_df)
    context.bot.send_message(chat_id=update.effective_chat.id, text=can_sell_response)


def _can_sell_msg_txt(can_sell_df):
    can_sell_df = can_sell_df.groupby(['can_sell', 'days_to_sell']).agg(list)
    can_sell_df = can_sell_df.reset_index()
    can_sell_df = can_sell_df.sort_values('days_to_sell', ascending=False)
    can_sell_summary = can_sell_df[['can_sell', 'days_to_sell', 'ticker']].values.tolist()
    can_sell_summary = [(can_sell_, days_to_sell, list(set(tickers))) for can_sell_, days_to_sell, tickers in can_sell_summary]
    can_sell_txt = Template(CAN_SELL_TEMPLATE).render({'can_sell_summary': can_sell_summary}).strip()
    return can_sell_txt
# endregion can_sell


# region conc
def asset_concentration(update, context):
    idea_mode, liquid_only = __parse_conc_inputs(context.args)
    last_close_df = asset_conc(idea_mode=idea_mode, liquid_only=liquid_only)
    asset_conc_str = _format_asset_concentration_output(last_close_df, liquid_only=liquid_only)
    code_start, code_length = determine_code_entity_location(asset_conc_str)
    context.bot.send_message(chat_id=update.effective_chat.id, text=asset_conc_str,
                             entities=[MessageEntity('code', code_start, code_length)])


def __parse_conc_inputs(args):
    idea_mode, total_pf = None, None
    split_args = [arg.strip() for arg in ' '.join(args).split(',')]
    if len(args) == 2:
        idea_mode, total_pf = [bool(arg) for arg in split_args]
    elif len(args) == 1:
        idea_mode = bool(split_args[0])
    # liquid_only = False shows only illiquid positions hence setting to None
    liquid_only = None if total_pf is True else True
    return idea_mode, liquid_only


def _format_asset_concentration_output(conc_df, liquid_only=False):
    asset_conc_template = Template(ASSET_CONCENTRATION_TEMPLATE)
    ticker_conc_list = [(row['ticker'], f"{row['concentration']:.1%}") for _, row in conc_df.iterrows()]
    ticker_concentrations = tabulate(ticker_conc_list, headers=['Ticker', 'Concentration (%)'],
                                     colalign=('left', 'right'))
    template_data = {'liquid_only': liquid_only, 'ticker_concentrations': ticker_concentrations}
    return asset_conc_template.render(template_data)
# endregion conc


# region size
def _parse_position_sizing_args(args):
    split_args = [arg.strip() for arg in ' '.join(args).split(',')]
    if len(split_args) in (3, 4):
        if len(split_args) == 3:
            ticker, period, loss_threshold_pct = split_args
            total_pf = False
        else:
            ticker, period, loss_threshold_pct, total_pf = split_args
            total_pf = bool(total_pf)
        loss_threshold_pct = parse_pct_input(loss_threshold_pct)
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
                                 [f'Vol over {period} days', f'{vol:.2%}']], colalign=('left', 'right'))
        reply_txt = f'''
Stats for a position in {ticker} that won't lose more than {loss_threshold_pct:.2%} of total portfolio value

{stats_output} 
        '''.strip()
        code_start, code_length = determine_code_entity_location(reply_txt)
    no_code_block = (code_start, code_length) == (None, None)
    msg_entity = None if no_code_block else MessageEntity('code', code_start, code_length)
    msg_entities = [msg_entity] if msg_entity else None
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_txt, entities=msg_entities)
# endregion size


# region returns
def returns(update, context):
    incl_values, liquid_only = _parse_returns_inputs(context.args)
    close_val_df = get_close_value(liquid_only=liquid_only, incl_return_col=True, aggregate=True)
    returns_reply = _format_returns_reply(close_val_df, incl_values)
    code_start, code_length = determine_code_entity_location(returns_reply)
    context.bot.send_message(chat_id=update.effective_chat.id, text=returns_reply,
                             entities=[MessageEntity('code', code_start, code_length)])


def _format_returns_reply(val_df, incl_values):
    val_df = val_df.rename(columns={'ticker': 'Ticker', 'buy_cost': 'BuyCost'})
    if incl_values:
        val_df = val_df[['Ticker', 'BuyCost', 'CloseValue', 'ReturnPct']]
        returns_list = [(row['Ticker'], f"{row['BuyCost']:,.0f}", f"{row['CloseValue']:,.0f}", f"{row['ReturnPct']:.1%}")
                        for _, row in val_df.iterrows()]
        col_align = ['left', 'right', 'right', 'right']
    else:
        val_df = val_df[['Ticker', 'ReturnPct']]
        returns_list = [(row['Ticker'], f"{row['ReturnPct']:.1%}") for _, row in val_df.iterrows()]
        col_align = ['left', 'right']
    returns_tbl = tabulate(returns_list, headers=val_df.columns.values, colalign=col_align)
    returns_reply = Template(RETURNS_TEMPLATE).render({'returns_tbl': returns_tbl})
    return returns_reply


def _parse_returns_inputs(args):
    incl_values, total_pf = None, None
    split_args = [arg.strip() for arg in ' '.join(args).split(',')]
    if len(split_args) == 2:
        incl_values, total_pf = [bool(arg) for arg in split_args]
    elif len(split_args) == 1:
        incl_values = bool(split_args[0])
    # liquid_only = False shows only illiquid positions hence setting to None
    liquid_only = None if total_pf is True else True
    return incl_values, liquid_only
# endregion returns
