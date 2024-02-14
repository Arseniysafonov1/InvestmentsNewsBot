from db_connection import Connection
from invest_api import InvestSession
import requests
ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
class CommonSession(object):
    def __init__(self, db_name, news_token):
        self._con = Connection(db_name)
        self._logged = dict()
        self._api = InvestSession(news_token)
        self._news = dict()
    def handler_message(self, userid, text, extras):
        login, state, token = self._con.get_user_info(userid)
        if state == 'reg_login':
            if (len(text) < 3) or (len(text) > 30):
                return "Логин должен содержать от 3 до 30 символов"
            for i in text:
                if i not in ALLOWED_CHARS:
                    return "В логине могут содержаться только английские буквы, цифры и знак подчеркивания"
            if self._con.check_login(text):
                return "Извините, этот логин уже занят"
            self._logged[userid] = text
            self._con.set_state(userid, "reg_pass")
            return "Хорошо. Теперь введите пароль: "
        elif state == 'reg_pass':
            if (len(text) < 3) or (len(text) > 30):
                return "Пароль должен содержать от 3 до 30 символов"
            for i in text:
                if i not in ALLOWED_CHARS:
                    return "В пароле могут содержаться только английские буквы, цифры и знак подчеркивания"
            self._con.registration(userid, self._logged[userid], text)
            self._con.set_state(userid, '')
            extras['keyboard'] = 'base-logged' if not token else 'token-logged'
            return "Регистрация прошла успешно!"
        elif state == "auth_login":
            if self._con.check_login(text):
                self._con.set_state(userid, "auth_pass")
                self._logged[userid] = text
                return "Введите пароль:"
            else:
                self._con.set_state(userid, '')
                extras['keyboard'] = 'non-logged'
                return "Такого логина нет. Попробуйте еще раз"
        elif state == "auth_pass":
            if self._con.auth(userid, self._logged[userid], text):
                self._con.set_state(userid, '')
                extras['keyboard'] = 'base-logged' if not token else 'token-logged'
                return "Вход прошел успешно"
            else:
                self._con.set_state(userid, '')
                extras['keyboard'] = 'non-logged'
                return "Неверный пароль. Попробуйте еще раз"
        elif state == "auth_token":
            if self._api.find_account(text):
                self._con.set_token(login, text)
                self._con.set_state(userid, '')
                extras['keyboard'] = 'token-logged'
                return "Аккаунт привязан успешно"
            else:
                self._con.set_state(userid, '')
                return "Аккаунт не удалось привязать"
        if text == "/exit":
            self._con.exit(userid)
            self._con.set_state(userid, '')
            extras['keyboard'] = 'non-logged'
            return "Вы вышли из аккаунта"
        elif text == "/reg":
            self._con.set_state(userid, 'reg_login')
            return "Введите логин:"
        elif text == "/auth":
            self._con.set_state(userid, 'auth_login')
            return "Введите логин:"
        elif text=="/news":
            if userid not in self._news.keys():
                self._news[userid] = self._api.find_news(token)
            t = self._news[userid].pop() if self._news[userid] else None
            if t:
                print(t)
                extras['keyboard'] = 'news-kb'
                return f"<a href=\"{t[1]}\">{t[0]}</a>"
            else:
                del self._news[userid]
                extras['keyboard'] = 'token-logged'
                return "Свежих новостей больше нет"
        elif text == "/close":
            self._news[userid] = None
            extras['keyboard'] = 'token-logged'
            return "Возврат к главному меню"
        elif text == "/token_auth":
            self._con.set_state(userid, 'auth_token')
            return """Проект находится в разработке и данные хранятся небезопасно! Пожалуйста, не передавайте токены от тех аккаунтов, которые боитесь потерять!
        Введите токен из приложения Тинькофф.Инвестиции (<a href = \"https://russianinvestments.github.io/investAPI/token/\">Как получить токен?</a>):"""
        elif text == "/help":
            extras['keyboard'] = 'non-logged'
            return "Войдите в аккаунт с помощью кнопки вход в аккаунт или зарегистрируйтесь для начала работы"
        elif text == "/start":
            extras['keyboard'] = 'non-logged'
            return """Привет! Я телеграм-бот по подборке новостей для инвесторов. Вот мои возможности:
        1. Предоставлять самые свежие новости из мира финансов, основываясь на вашем пакете акций и интересующих категориях.
        2. Предоставлять недавние новости по выбранной категории/компаниям
        3. Осуществлять персонализированную рассылку новостей в выбранное вами время
        4. Формировать сводку о ваших инвестициях и их доходе за выбранный период
        """
        if login:
            extras['keyboard'] = 'base-logged' if not token else 'token-logged'
            return "Извините, я не понимаю ваш запрос, если вам непонятны команды возпользуйтесь кнопкой помощь"
        extras['keyboard'] = 'non-logged'
        return "Извините, я не понимаю ваш запрос, если вам непонятны команды возпользуйтесь кнопкой помощь"