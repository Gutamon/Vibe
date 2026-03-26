from app.views import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True 會在程式碼修改時自動重新載入，適合開發時使用
    app.run(host="0.0.0.0", port=5000, debug=True)