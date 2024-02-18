import sqlite3

class UserRepository:
    def __init__(self):
        self.conn = sqlite3.connect("sudden-attack.db")
        self.cursor = self.conn.cursor()

    def update_refresh_token(self, email: str, refresh_token: str):
        self.cursor.execute(
            "UPDATE user SET refresh_token=? WHERE email=?", (refresh_token, email)
        )
        self.conn.commit()