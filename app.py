from flask import Flask, render_template, abort, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import session  # 위에 import 추가

import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # 아무 문자열 OK

# ✅ 데이터베이스 설정
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'products.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ✅ SQLAlchemy 객체 생성
db = SQLAlchemy(app)

# ✅ 여기! 이 아래에 모델 정의
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

# 임시 상품 목록
# products = [
#     {"id": 1, "name": "노트북", "price": 1000000},
#     {"id": 2, "name": "무선 이어폰", "price": 150000},
#     {"id": 3, "name": "기계식 키보드", "price": 80000},
# ]

@app.route("/")
def product_list():
    products = Product.query.all()
    return render_template("products.html", products=products)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        abort(404)
    return render_template("product_detail.html", product=product)

@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")

        if not name or not price or not price.isdigit():
            return "입력이 올바르지 않습니다.", 400

        new_product = Product(name=name, price=int(price))
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for("product_list"))

    return render_template("add_product.html")

@app.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("product_list"))

@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")

        if not name or not price or not price.isdigit():
            return "입력이 올바르지 않습니다.", 400

        product.name = name
        product.price = int(price)
        db.session.commit()

        return redirect(url_for("product_list"))

    return render_template("edit_product.html", product=product)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # 예시: 관리자 계정은 username: admin, password: 1234
        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect(url_for("product_list"))
        else:
            return "로그인 실패!", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("product_list"))

# ✅ run은 항상 마지막 줄!
if __name__ == "__main__":
    app.run(debug=True)
