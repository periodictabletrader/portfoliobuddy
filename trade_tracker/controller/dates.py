import datetime
from calendar import monthrange


def _get_current_period(period_type):
    today = datetime.date.today()
    current_month = 1
    current_year = today.year
    if period_type.lower() == 'm':
        current_month = today.month
    return current_month, current_year


def get_period_start_and_end(period_type):
    month, year = _get_current_period(period_type)
    end_month = month
    if period_type.lower() == 'y':
        end_month = 12
    period_start_date = datetime.date(year, month, 1)
    _, end_date = monthrange(year, end_month)
    period_end_date = datetime.date(year, end_month, end_date)
    return period_start_date, period_end_date


def get_first_day_of_month_from_date(date_input):
    date_year = date_input.year
    date_month = date_input.month
    first_day_of_dates_month = datetime.date(date_year, date_month, 1)
    return first_day_of_dates_month


def parse_date_str(date_str, date_fmt='%Y-%m-%d'):
    try:
        parsed_date = datetime.datetime.strptime(date_str, date_fmt).date()
    except TypeError:
        parsed_date = None
    return parsed_date
