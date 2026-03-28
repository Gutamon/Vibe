from werkzeug.security import generate_password_hash, check_password_hash
from app.models.db import get_db
from app.models.category import CategoryModel

class UserModel:
    def create_user(self, username, password):
        with get_db() as conn:
            cursor = conn.cursor()
            # 檢查帳號是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return None 
            
            hashed = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
            user_id = cursor.lastrowid
            
        # 👇 將以下兩行往左縮排，移出 with get_db() as conn: 的區塊 👇
        # 這樣就能確保 users 的寫入已經 commit 並且釋放了資料庫鎖定
        CategoryModel().create_defaults(user_id)
        return user_id

    def authenticate(self, username, password):
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user['password_hash'], password):
                return dict(user)
            return None