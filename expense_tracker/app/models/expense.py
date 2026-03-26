from app.views import mongo
from bson import ObjectId
from datetime import datetime


class ExpenseModel:
    """所有與 expenses collection 相關的資料庫操作。"""

    COLLECTION = "expenses"

    @property
    def col(self):
        return mongo.db[self.COLLECTION]

    # ── Create ────────────────────────────────────────────────────────────────

    def create(self, title: str, amount: float, category: str, date: str, note: str = "") -> str:
        """新增一筆支出，回傳新文件的 id 字串。"""
        doc = {
            "title": title,
            "amount": float(amount),
            "category": category,
            "date": datetime.strptime(date, "%Y-%m-%d"),
            "note": note,
            "created_at": datetime.utcnow(),
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_all(self, sort_by: str = "date", order: int = -1) -> list:
        """取得所有支出，預設依日期降冪排序。"""
        docs = self.col.find().sort(sort_by, order)
        return [self._serialize(d) for d in docs]

    def get_by_id(self, expense_id: str) -> dict | None:
        doc = self.col.find_one({"_id": ObjectId(expense_id)})
        return self._serialize(doc) if doc else None

    def get_by_category(self, category: str) -> list:
        docs = self.col.find({"category": category}).sort("date", -1)
        return [self._serialize(d) for d in docs]

    def get_monthly_summary(self) -> list:
        """
        回傳每個月的支出總額：
        [{"year": 2024, "month": 5, "total": 12345.0}, ...]
        """
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"},
                    },
                    "total": {"$sum": "$amount"},
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        results = self.col.aggregate(pipeline)
        return [
            {"year": r["_id"]["year"], "month": r["_id"]["month"], "total": r["total"]}
            for r in results
        ]

    def get_category_summary(self) -> list:
        """
        回傳各類別的支出總額：
        [{"category": "餐飲", "total": 5000.0}, ...]
        """
        pipeline = [
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            {"$sort": {"total": -1}},
        ]
        results = self.col.aggregate(pipeline)
        return [{"category": r["_id"], "total": r["total"]} for r in results]

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, expense_id: str, data: dict) -> bool:
        """更新指定支出，回傳是否成功。"""
        update_fields = {}
        if "title" in data:
            update_fields["title"] = data["title"]
        if "amount" in data:
            update_fields["amount"] = float(data["amount"])
        if "category" in data:
            update_fields["category"] = data["category"]
        if "date" in data:
            update_fields["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
        if "note" in data:
            update_fields["note"] = data["note"]

        if not update_fields:
            return False

        result = self.col.update_one(
            {"_id": ObjectId(expense_id)}, {"$set": update_fields}
        )
        return result.modified_count > 0

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete(self, expense_id: str) -> bool:
        result = self.col.delete_one({"_id": ObjectId(expense_id)})
        return result.deleted_count > 0

    # ── Helper ────────────────────────────────────────────────────────────────

    @staticmethod
    def _serialize(doc: dict) -> dict:
        """將 MongoDB 文件轉為可 JSON 序列化的 dict。"""
        doc["id"] = str(doc.pop("_id"))
        doc["date"] = doc["date"].strftime("%Y-%m-%d") if isinstance(doc.get("date"), datetime) else doc.get("date", "")
        doc["created_at"] = (
            doc["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(doc.get("created_at"), datetime)
            else doc.get("created_at", "")
        )
        return doc
