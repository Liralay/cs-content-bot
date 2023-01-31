import sqlite3
import logging
logging.basicConfig(level=logging.INFO)

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM distr WHERE user_id = ?", (user_id,)).fetchmany(1)
            return bool(len(result))

    def add_user(self, user_id):
        with self.connection:
            try:
                return self.cursor.execute("INSERT INTO distr (user_id) VALUES (?)", (user_id,))
            except:
                pass

    def set_active(self, user_id, active):
        with self.connection:
            logging.info(f'user_id {user_id}, active {active}')
            return self.cursor.execute("UPDATE distr SET active = ? WHERE user_id = ?", (active, user_id))

    def get_user(self):
        with self.connection:
            return self.cursor.execute("SELECT user_id, active FROM distr").fetchall()

    def is_admin(self, user_id):
        with self.connection:
            try:
                result = self.cursor.execute(("SELECT active FROM admin_users WHERE user_id = ?"), (user_id,)).fetchmany(1)[0][0]
                if result == 1:
                    return True
                else:
                    return False
            except:
                return False

    def grant_admin(self, user_id):
         with self.connection:
            try:
                return self.cursor.execute("INSERT INTO admin_users (user_id) VALUES (?)", (user_id,))
            except Exception as e:
                return e
                    

    def revoke_admin(self, user_id, active):
        with self.connection:
            logging.info(f'user_id {user_id}, active {active}')
            return self.cursor.execute("UPDATE admin_users SET active = ? WHERE user_id = ?", (active, user_id))

    def number_of_users(self):
        with self.connection:
            return int(self.cursor.execute("SELECT COUNT(id) FROM distr WHERE active = 1").fetchall()[0][0])

    def get_user_ud(self, id):
        with self.connection:
            try:
                result = self.cursor.execute(("SELECT user_id FROM distr WHERE id = ?"), (id,)).fetchmany(1)[0][0]
                return result 
            except Exception as e:
                return str (f"Ошибка базы данных. Тип ошибки: {e}")

    def is_active(self, id):
        with self.connection:
            result = self.cursor.execute(("SELECT active FROM distr WHERE id = ?"), (id,)).fetchmany(1)[0][0]
            if result == 1:
                return True
            else:
                return False

    def is_active_uid(self, user_id):
        with self.connection:
            result = self.cursor.execute(("SELECT active FROM distr WHERE user_id = ?"), (user_id,)).fetchmany(1)[0][0]
            if result == 1:
                return True
            else:
                return False


