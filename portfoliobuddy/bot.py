from telegram.ext import CommandHandler, Updater

from portfoliobuddy.controller.user import user_exists
from portfoliobuddy.credentials import access_token
from portfoliobuddy.view.portfolio_stats import can_sell, asset_concentration, asset_concentration_liquid


def start(update, context):
    user_id = update.effective_user.id
    does_user_exist = user_exists(user_id)
    if not does_user_exist:
        start_txt = 'Sorry. This Bot is intended for the author of this bot\'s personal use. ' \
                    'Please look for an alternative.'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=start_txt)


def register_commands(dispatcher):
    last_handler = CommandHandler('can_sell', can_sell)
    dispatcher.add_handler(last_handler)
    asset_conc = CommandHandler('conc', asset_concentration)
    dispatcher.add_handler(asset_conc)
    asset_conc_liquid = CommandHandler('conc_liquid', asset_concentration_liquid)
    dispatcher.add_handler(asset_conc_liquid)
    return dispatcher


def setup_and_start_bot():
    updater = Updater(token=access_token, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    dispatcher = register_commands(dispatcher)

    # # Jobs
    # job_context = CallbackContext(dispatcher)
    # job_context._chat_data = {'id': get_chat_id()}
    # end_of_month_report_time = datetime.time(8, 0, 0, 0, pytz.timezone('Europe/London'))
    # job_queue.run_daily(end_of_month_report, end_of_month_report_time, context=job_context)

    updater.start_polling()
    updater.idle()


def main():
    setup_and_start_bot()


if __name__ == '__main__':
    main()
