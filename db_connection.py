import sqlite3 as sql


class Connection(object):
    def __init__(self, connection_path):
        self._con = sql.connect(connection_path, check_same_thread=False)
        with self._con as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS `users` (login VARCHAR PRIMARY KEY, password VARCHAR, token VARCHAR);")
            cur.execute("CREATE TABLE IF NOT EXISTS `tg_to_users` (tg_id INTEGER PRIMARY KEY, login VARCHAR, state VARCHAR);")
            con.commit()
    def check_login(self, login):
        with self._con as con:

            cur = con.cursor()
            cur.execute(f"SELECT login FROM users WHERE login=\'{login}\'")
            if len(cur.fetchall()):
                return 1
        return 0
    def registration(self, userid, login, password):
        with self._con as con:
            cur = con.cursor()
            if self.check_login(login):
                return -1
            cur.execute(f"INSERT INTO users values(\'{login}\', \'{password}\', NULL)")
            cur.execute(f"UPDATE tg_to_users SET login=\'{login}\' WHERE tg_id={userid}")
            con.commit()
            return 1
    def auth(self, userid, login, password):
        with self._con as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM  users WHERE login=\'{login}\' AND password=\'{password}\'")
            d = cur.fetchall()
            if not len(d):
                return 0
            cur.execute(f"UPDATE tg_to_users SET login=\'{login}\' WHERE tg_id={userid}")
            con.commit()
            return 1

    def get_user_info(self, userid):
        with self._con as con:
            cur = con.cursor()
            cur.execute(f"SELECT login, state FROM tg_to_users where tg_id={userid}")
            d = cur.fetchall()
            if not len(d):
                return '', '', ''
            login, state = d[0]
            token = ''
            cur.execute(f"SELECT token FROM users WHERE login=\'{login}\'")
            t = cur.fetchall()
            if len(t):
                token = t[0][0]
            return login, state, token
    def set_state(self, userid, state):
        with self._con as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM tg_to_users WHERE tg_id={userid}")
            d = cur.fetchall()
            if len(d) == 0:
                cur.execute(f"INSERT INTO tg_to_users VALUES ({userid}, NULL, \'{state}\');")
            else:
                cur.execute(f"UPDATE tg_to_users SET state=\'{state}\' WHERE tg_id={userid}")
            con.commit()
    def set_token(self, login, token):
        with self._con as con:
            cur = con.cursor()
            cur.execute(f"UPDATE users SET token=\'{token}\' WHERE login={login}")
            con.commit()

    def exit(self, userid):
        with self._con as con:
            cur = con.cursor()
            cur.execute(f"UPDATE tg_to_users SET login=NULL WHERE tg_id={userid}")
            con.commit()
