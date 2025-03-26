# user_service.py
from db_utils import get_db_connection
import bcrypt

class UserService:
    @staticmethod
    def create_user(username, password):
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        with get_db_connection() as conn:
            try:
                conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                           (username, hashed_pw))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    @staticmethod
    def verify_user(username, password):
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row and bcrypt.checkpw(password.encode(), row[0]):
                return True
        return False

    @staticmethod
    def save_health_data(user_id, sbp, dbp, glucose, triglycerides):
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO health_records 
                (user_id, sbp, dbp, glucose, triglycerides)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, sbp, dbp, glucose, triglycerides))
            conn.commit()