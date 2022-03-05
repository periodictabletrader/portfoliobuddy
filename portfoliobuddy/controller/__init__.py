from portfoliobuddy.model import session, Account, Trade


def get_accounts():
    db_session = session()
    results = db_session.query(Account)
    return [result.account for result in results]


def _format_trade_for_keyboard(trade_row, acc_map):
    ticker = trade_row.ticker
    qty = trade_row.qty
    trade_date = trade_row.date.strftime('%Y%m')
    account = acc_map[trade_row.accid]
    return f'{trade_date} - {ticker}, {qty:.0f}, {account}'


def get_trade_strs():
    db_session = session()
    accounts = get_accounts()
    results = db_session.query(Trade)
    formatted_trades = [_format_trade_for_keyboard(result, accounts) for result in results]
    return formatted_trades
