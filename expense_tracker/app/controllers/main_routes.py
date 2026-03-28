from flask import Blueprint, render_template, request, jsonify, abort, session, redirect
from app.models.expense import ExpenseModel
from app.models.category import CategoryModel

main_bp = Blueprint("main", __name__)
expense_model = ExpenseModel()
category_model = CategoryModel()

@main_bp.before_request
def require_login():
    if 'user_id' not in session:
        if request.path.startswith('/api/'):
            return jsonify({"error": "未登入"}), 401
        return redirect('/login')

@main_bp.route("/")
def index():
    user_id = session['user_id']
    expenses = expense_model.get_all(user_id)
    total = sum(e["amount"] for e in expenses)
    categories = category_model.get_by_user(user_id)
    cat_names = [c["name"] for c in categories]
    return render_template("index.html", expenses=expenses, categories=cat_names, total=total, username=session['username'])

@main_bp.route("/charts")
def charts():
    return render_template("charts.html", username=session['username'])

@main_bp.route("/api/expenses", methods=["GET"])
def api_list():
    return jsonify(expense_model.get_all(session['user_id']))

@main_bp.route("/api/expenses", methods=["POST"])
def api_create():
    data = request.get_json(force=True)
    required = ("title", "amount", "category", "date")
    if not all(k in data for k in required): abort(400, description="缺少必要欄位")

    new_id = expense_model.create(
        user_id=session['user_id'],
        title=data["title"],
        amount=data["amount"],
        category=data["category"],
        date=data["date"],
        note=data.get("note", ""),
    )
    return jsonify({"success": True, "id": new_id}), 201

@main_bp.route("/api/expenses/<expense_id>", methods=["GET"])
def api_get(expense_id):
    doc = expense_model.get_by_id(expense_id, session['user_id'])
    if not doc: abort(404, description="找不到此筆支出")
    return jsonify(doc)

@main_bp.route("/api/expenses/<expense_id>", methods=["PUT"])
def api_update(expense_id):
    data = request.get_json(force=True)
    if not expense_model.update(expense_id, session['user_id'], data):
        abort(404, description="更新失敗或找不到此筆支出")
    return jsonify({"success": True})

@main_bp.route("/api/expenses/<expense_id>", methods=["DELETE"])
def api_delete(expense_id):
    if not expense_model.delete(expense_id, session['user_id']):
        abort(404, description="找不到此筆支出")
    return jsonify({"success": True})

@main_bp.route("/api/charts/monthly")
def api_monthly():
    return jsonify(expense_model.get_monthly_summary(session['user_id']))

@main_bp.route("/api/charts/category")
def api_category():
    return jsonify(expense_model.get_category_summary(session['user_id']))

@main_bp.app_errorhandler(400)
def bad_request(e): return jsonify({"error": str(e.description)}), 400
@main_bp.app_errorhandler(404)
def not_found(e): return jsonify({"error": str(e.description)}), 404