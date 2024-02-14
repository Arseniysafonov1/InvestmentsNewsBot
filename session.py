import telebot
from logic import CommonSession
from telebot import types

def start_session(params):
    com_to_com = {
        "Регистрация":"/reg",
        "Вход в аккаунт":"/auth",
        "Помощь":"/help",
        "Выйти":"/exit",
        "Привязать Тинькофф.Инвестиции":"/token_auth",
        "Сменить аккаунт Тинькофф.Инвестиций":"/token_auth",
        "Еще новости":"/news",
        "Новости":"/news",
        "Закрыть":"/close"
    }
    bot = None
    logic = None
    none_markup = types.ReplyKeyboardRemove()
    non_logged_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    non_logged_kb.add(types.KeyboardButton("Регистрация"))
    non_logged_kb.add(types.KeyboardButton("Вход в аккаунт"))
    non_logged_kb.add(types.KeyboardButton("Помощь"))
    logged_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    logged_kb.add(types.KeyboardButton("Привязать Тинькофф.Инвестиции"))
    logged_kb.add(types.KeyboardButton("Выйти"))
    token_logged_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    token_logged_kb.add(types.KeyboardButton("Новости"))
    token_logged_kb.add(types.KeyboardButton("Сменить аккаунт Тинькофф.Инвестиций"))
    token_logged_kb.add(types.KeyboardButton("Выйти"))
    news_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    news_kb.add(types.KeyboardButton("Еще новости"))
    news_kb.add(types.KeyboardButton("Закрыть"))
    try:
        _token = params['token']
        _db_name = params['db_name']
        _news_token = params['news_token']
        logic = CommonSession(_db_name, _news_token)
        bot = telebot.TeleBot(token=_token)
    except IndexError as ie:
        raise Exception('Invalid params', ie.args)

    @bot.message_handler()
    def _handler_message(message):
        t = com_to_com.get(message.text, message.text)
        extras = {
            'keyboard':None
        }
        txt = logic.handler_message(message.from_user.id, t, extras)
        reply_markup = none_markup
        if extras['keyboard'] == 'non-logged':
            reply_markup = non_logged_kb
        elif extras['keyboard'] == 'base-logged':
            reply_markup = logged_kb
        elif extras['keyboard'] == 'token-logged':
            reply_markup = token_logged_kb
        elif extras['keyboard'] == 'news-kb':
            reply_markup = news_kb
        bot.send_message(message.chat.id, text=txt, reply_markup=reply_markup, parse_mode='HTML')

    bot.polling(none_stop=True)
