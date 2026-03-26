import sqlite3
from datetime import datetime

class ExpenseModel:
    """所有與 expenses 資料庫相關的操作 (使用 SQLite)"""
    
    DB_PATH = "expenses.db"

    def __init__(self):
        self._init_db()

    def get_db(self):
        conn = sqlite3.connect(self.DB_PATH)
        conn.row_factory = sqlite3.Row  # 讓回傳結果可以像 dict 一樣操作
        return conn

    def _init_db(self):
        with self.get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL
                )
            ''')

    # ── Create ────────────────────────────────────────────────────────────────

    def create(self, title: str, amount: float, category: str, date: str, note: str = "") -> str:
        with self.get_db() as conn:
            cursor = conn.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO expenses (title, amount, category, date, note, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, float(amount), category, date, note, created_at))
            return str(cursor.lastrowid)

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_all(self, sort_by: str = "date", order: int = -1) -> list:
        order_dir = "DESC" if order == -1 else "ASC"
        # 避免 SQL Injection，限制 sort_by 的白名單
        if sort_by not in ["date", "amount", "category", "created_at"]:
            sort_by = "date"
            
        with self.get_db() as conn:
            rows = conn.execute(f'SELECT * FROM expenses ORDER BY {sort_by} {order_dir}').fetchall()
            return [dict(row) for row in rows]

    def get_by_id(self, expense_id: str) -> dict | None:
        with self.get_db() as conn:
            row = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
            return dict(row) if row else None

    def get_monthly_summary(self) -> list:
        with self.get_db() as conn:
            rows = conn.execute('''
                SELECT 
                    CAST(strftime('%Y', date) AS INTEGER) as year,
                    CAST(strftime('%m', date) AS INTEGER) as month,
                    SUM(amount) as total
                FROM expenses
                GROUP BY year, month
                ORDER BY year, month
            ''').fetchall()
            return [{"year": r["year"], "month": r["month"], "total": r["total"]} for r in rows]

    def get_category_summary(self) -> list:
        with self.get_db() as conn:
            rows = conn.execute('''
                SELECT category, SUM(amount) as total
                FROM expenses
                GROUP BY category
                ORDER BY total DESC
            ''').fetchall()
            return [{"category": r["category"], "total": r["total"]} for r in rows]

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, expense_id: str, data: dict) -> bool:
        update_fields = []
        values = []
        
        for key in ["title", "amount", "category", "date", "note"]:
            if key in data:
                update_fields.append(f"{key} = ?")
                val = float(data[key]) if key == "amount" else data[key]
                values.append(val)

        if not update_fields:
            return False

        values.append(expense_id)
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE expenses SET {', '.join(update_fields)} WHERE id = ?
            ''', values)
            return cursor.rowcount > 0

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete(self, expense_id: str) -> bool:
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            return cursor.rowcount > 0