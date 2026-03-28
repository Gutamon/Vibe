from app.models.db import get_db

class CategoryModel:
    DEFAULT_CATEGORIES = ["餐飲", "交通", "娛樂", "購物", "醫療", "住宿", "教育", "其他"]

    def create_defaults(self, user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            for cat in self.DEFAULT_CATEGORIES:
                cursor.execute("INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, cat))

    def get_by_user(self, user_id):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM categories WHERE user_id = ?", (user_id,)).fetchall()
            return [dict(r) for r in rows]

    def create(self, user_id, name):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, name))
            return cursor.lastrowid

    def update(self, cat_id, user_id, name):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE categories SET name = ? WHERE id = ? AND user_id = ?", (name, cat_id, user_id))
            return cursor.rowcount > 0

    def delete(self, cat_id, user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ? AND user_id = ?", (cat_id, user_id))
            return cursor.rowcount > 0