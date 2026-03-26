from flask import Blueprint, render_template, request, jsonify, abort
from app.models.expense import ExpenseModel

main_bp = Blueprint("main", __name__)
expense_model = ExpenseModel()

CATEGORIES = ["餐飲", "交通", "娛樂", "購物", "醫療", "住宿", "教育", "其他"]


# ── Pages ─────────────────────────────────────────────────────────────────────

@main_bp.route("/")
def index():
    expenses = expense_model.get_all()
    total = sum(e["amount"] for e in expenses)
    return render_template("index.html", expenses=expenses, categories=CATEGORIES, total=total)


@main_bp.route("/charts")
def charts():
    return render_template("charts.html")


# ── API: Expenses CRUD ────────────────────────────────────────────────────────

@main_bp.route("/api/expenses", methods=["GET"])
def api_list():
    expenses = expense_model.get_all()
    return jsonify(expenses)


@main_bp.route("/api/expenses", methods=["POST"])
def api_create():
    data = request.get_json(force=True)
    required = ("title", "amount", "category", "date")
    if not all(k in data for k in required):
        abort(400, description="缺少必要欄位")

    new_id = expense_model.create(
        title=data["title"],
        amount=data["amount"],
        category=data["category"],
        date=data["date"],
        note=data.get("note", ""),
    )
    return jsonify({"success": True, "id": new_id}), 201


@main_bp.route("/api/expenses/<expense_id>", methods=["GET"])
def api_get(expense_id):
    doc = expense_model.get_by_id(expense_id)
    if not doc:
        abort(404, description="找不到此筆支出")
    return jsonify(doc)


@main_bp.route("/api/expenses/<expense_id>", methods=["PUT"])
def api_update(expense_id):
    data = request.get_json(force=True)
    success = expense_model.update(expense_id, data)
    if not success:
        abort(404, description="更新失敗或找不到此筆支出")
    return jsonify({"success": True})


@main_bp.route("/api/expenses/<expense_id>", methods=["DELETE"])
def api_delete(expense_id):
    success = expense_model.delete(expense_id)
    if not success:
        abort(404, description="找不到此筆支出")
    return jsonify({"success": True})


# ── API: Chart Data ───────────────────────────────────────────────────────────

@main_bp.route("/api/charts/monthly")
def api_monthly():
    data = expense_model.get_monthly_summary()
    return jsonify(data)


@main_bp.route("/api/charts/category")
def api_category():
    data = expense_model.get_category_summary()
    return jsonify(data)


# ── Error Handlers ────────────────────────────────────────────────────────────

@main_bp.app_errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


@main_bp.app_errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404
