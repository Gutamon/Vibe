from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.user import UserModel

auth_bp = Blueprint("auth", __name__)
user_model = UserModel()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json(force=True)
        user = user_model.authenticate(data.get("username"), data.get("password"))
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "帳號或密碼錯誤"}), 401
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json(force=True)
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"success": False, "error": "請填寫完整資訊"}), 400
            
        user_id = user_model.create_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "帳號已存在"}), 400
    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.login'))