from const_variables import *
import telegram
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters, CallbackQueryHandler,
)

from database import UsersDB

logger = logging.getLogger('main')
logger.setLevel(GLOBAL_LOGGER_LEVEL)

users = UsersDB()

NAME = range(1)


def get_user_keyboard():
    keyboard = [['Показать список']]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_mark_watched_keyboard():
    keyboard = [[InlineKeyboardButton('Отметить просмотренные', callback_data='delete_watched')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_list_keyboard(user_list):
    keyboard = []

    for name in user_list:
        keyboard.append([name])
    keyboard.append(['Удалить все'])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def send_start_msg(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    logger.info(f'Новое сообщение: /start или /help. пользователь:{user_id}')

    users.add_user(user_id)

    update.message.reply_text('Этот бот может отслеживать посылки через сервис Почта России\n'
                              'Чтобы узнать где находится ваша посылка, просто введие номер отправления.\n'
                              'Техподдержка: телеграм t.me/dragon_np почта: dragonnp@yandex.ru',
                              disable_web_page_preview=True)

    update.message.reply_text('Пример', reply_markup=get_user_keyboard())


def send_list(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    logger.info(f'Отправка списка. пользователь:{user_id}')

    user_list = users.get_list(user_id)

    formatted_user_list = ''
    for name in user_list:
        formatted_user_list += f'[{name}]({user_list[name]})\n\n'

    update.message.reply_text(f'*Ваш список:*\n{formatted_user_list}',
                              parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True,
                              reply_markup=get_mark_watched_keyboard())


def delete_watched(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    logger.debug(f'Удаление просмотренных ссылок. пользователь:{user_id}')

    user_list = users.get_list(user_id)

    query.from_user.send_message(text='Выберите, что хотите удалить',
                                 reply_markup=get_list_keyboard(user_list),
                                 parse_mode=telegram.ParseMode.MARKDOWN)


def remove_watched(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    name = update.message.text

    if name == 'Удалить все':
        users.remove_all(user_id)
        logger.debug(f'Удаление всех ссылок. пользователь:{user_id}')
        update.message.reply_text('Все ссылки удалены', reply_markup=get_user_keyboard())
        return

    res = users.check_link(user_id, name)

    if not res:
        update.message.reply_text('Такой ссылки не существует', reply_markup=get_user_keyboard())
    else:
        logger.debug(f'Удаление ссылки. пользователь:{user_id}, имя:{name}')
        users.remove_link(user_id, name)
        update.message.reply_text('Ссылка удалена', reply_markup=get_user_keyboard())


def start_to_add_link(update: Update, context: CallbackContext) -> range:
    user_id = update.message.from_user.id
    context.user_data['link'] = update.message.text

    logger.debug(f'Добавление ссылки в список. пользователь:{user_id}, ссылка:{update.message.text}')

    keyboard = [['Назад']]

    update.message.reply_text('Введите название для этой ссылки',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return NAME


def add_link(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    link = context.user_data['link']
    name = update.message.text

    logger.info(f'Добавление ссылки в список. пользователь:{user_id}, название:{name}, ссылка:{link}')

    res, message = users.add_link(user_id, link, name)

    text = 'Ссылка добавлена'
    if not res:
        text = message

    update.message.reply_text(text, reply_markup=get_user_keyboard())
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    logger.debug(f'Пользователь отменил добавление ссылки, id пользователя:{user_id}')

    del context.user_data['link']
    return ConversationHandler.END


def error_callback(update: Update, context: CallbackContext):
    error: Exception = context.error

    logger.error(error)
    update.message.reply_text(
        'Произошла ошибка. Пожалуйста, свяжитесь со мной через телеграм t.me/dragon_np или через почту dragonnp@yandex.ru')


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create the Updater and pass it your bot token.
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', send_start_msg))
    dispatcher.add_handler(CommandHandler('help', send_start_msg))
    dispatcher.add_handler(MessageHandler(Filters.text('Показать список'), send_list))
    dispatcher.add_handler(CallbackQueryHandler(delete_watched))

    add_link_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'https://'), start_to_add_link)],
        states={
            NAME: [MessageHandler(Filters.text, add_link)]
        },
        fallbacks=[MessageHandler(Filters.text('Назад'), cancel)]
    )

    dispatcher.add_handler(add_link_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, remove_watched))
    dispatcher.add_error_handler(error_callback)

    # Start the Bot
    updater.start_polling()

    logger.info('Бот работает')
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
