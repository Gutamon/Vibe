from flask import Blueprint, render_template, request, jsonify, session, abort, redirect
from app.models.category import CategoryModel

category_bp = Blueprint("category", __name__)
category_model = CategoryModel()

@category_bp.before_request
def require_login():
    if 'user_id' not in session:
        if request.path.startswith('/api/'):
            return jsonify({"error": "未登入"}), 401
        return redirect('/login')

@category_bp.route("/categories")
def manage_categories():
    categories = category_model.get_by_user(session['user_id'])
    return render_template("categories.html", categories=categories, username=session.get('username'))

@category_bp.route("/api/categories", methods=["POST"])
def api_create_category():
    data = request.get_json(force=True)
    name = data.get("name")
    if not name: abort(400, "缺少類別名稱")
    new_id = category_model.create(session['user_id'], name)
    return jsonify({"success": True, "id": new_id}), 201

@category_bp.route("/api/categories/<int:cat_id>", methods=["PUT"])
def api_update_category(cat_id):
    data = request.get_json(force=True)
    if category_model.update(cat_id, session['user_id'], data.get("name")):
        return jsonify({"success": True})
    abort(404, "更新失敗")

@category_bp.route("/api/categories/<int:cat_id>", methods=["DELETE"])
def api_delete_category(cat_id):
    if category_model.delete(cat_id, session['user_id']):
        return jsonify({"success": True})
    abort(404, "刪除失敗")