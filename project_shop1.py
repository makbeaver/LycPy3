import sqlite3

from flask import Flask, render_template, redirect, \
    request, url_for, Request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import InvalidRequestError

request: Request

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///shop.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)  # Подключение базы данных
bas = {}  # Словарь с корзиной пользователя
user = []


class Item(db.Model):  # класс, описывающий SQL таблицу с товарами
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)
    photo = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title


class Users(db.Model):  # класс, описывающий SQL-таблицу с пользователями
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.String(100), nullable=False)


@app.route('/clear_cart')  # Очистка корзины
def clear_cart():
    bas.clear()
    return redirect('/cart')


@app.route('/')  # Выход пользователя из аккаунта
def index():
    items = Item.query.order_by(Item.price).all()
    user.clear()
    clear_cart()
    return render_template('index.html', data=items, name='', prod=bas)


@app.route('/api/del_item/<item_id>')  # Удаление товара администратором
def del_item(item_id: int):
    con = sqlite3.connect('shop.db')
    cur = con.cursor()
    cur.execute(f"""DELETE from item
    where id = '{item_id}' """)
    con.commit()
    con.close()
    return redirect('/login')


# Добавление товара в корзину -- кнопка "Купить"


@app.route('/api/buy_item/<item_id>')
def buy_item(item_id):
    con = sqlite3.connect('shop.db')
    cur = con.cursor()
    x = cur.execute(f"""SELECT price from item
    where title = '{item_id}' """).fetchall()
    con.close()
    if item_id not in bas:
        bas[item_id] = [1, *x[0]]
    else:
        bas[item_id] = [bas[item_id][0] + 1, *x[0]]
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items, name='', prod=bas)


@app.route('/api/del_item_cart/<item_id>')  # Уменьшение количества товара
def del_item_cart(item_id):
    con = sqlite3.connect('shop.db')
    cur = con.cursor()
    x = cur.execute(f"""SELECT price from item
    where title = '{item_id}' """).fetchall()
    con.close()
    if item_id not in bas or bas[item_id][0] == 0:
        if bas[item_id][0] == 0:
            del (bas[item_id])
    else:
        bas[item_id] = [bas[item_id][0] - 1, *x[0]]
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items, name='', prod=bas)


@app.route('/cart')  # Переход в корзину
def cart():
    if len(user) > 0:
        return render_template('basket.html', products=bas, name=user[0],
                               total=sum(map(lambda i: i[1][0] * i[1][1], bas.items())))
    else:
        return render_template('basket.html', products=bas, name="Вы не авторизованы", total=sum(map(lambda i: i[1][0] * i[1][1],
                                                                                      bas.items())))


@app.route('/account')  # Переход в раздел "Управление аккаунтом"
def account():
    if len(user) > 0:
        return render_template('account.html', name=user[0])
    else:
        return render_template('account.html', name='---')


@app.route('/about')  # Переход в раздел "Контакты"
def about():
    if len(user) > 0:
        return render_template('about.html', name=user[0])
    else:
        return render_template('about.html', name='---')


@app.route('/reg', methods=['POST'])  # Регистрация нового пользователя
def sign_up():
    form = request.form
    email = request.form['email']
    password = request.form['psw']
    password_proof = request.form['psw_proof']
    sex = request.form['sex']
    if password == password_proof:
        print(
            f'''\x1b[1m{form["email"]}\x1b[m, a \x1b[92m{form["sex"]}\x1b[m with password \x1b[91m{form["psw"]}\x1b[m''')
        new_user = Users(email=email, password=password, sex=sex)
        try:
            db.session.add(new_user)
            db.session.commit()
            items = Item.query.order_by(Item.price).all()
            user.append(email)
            clear_cart()  # Очищаем корзину
            print(bas)
            return render_template('index.html', data=items, name=email, prod=bas)
        except InvalidRequestError:
            return "Ошибка!"
    else:
        return redirect('/')


@app.route('/home')  # Переход на главную страницу
def home():
    items = Item.query.order_by(Item.price).all()
    if len(user) > 0:
        return render_template('index.html', data=items, name=user[0], prod=bas)
    else:
        return render_template('index.html', data=items, name='', prod=bas)


@app.route('/change_psw', methods=['POST'])  # Изменение пароля пользователем
def change_psw():
    old_psw = request.form['old_psw']
    new_psw = request.form['new_psw']
    new_psw2 = request.form['new_psw2']
    d_users = {}
    for el in Users.query.order_by(Users.email).all():
        d_users[el.email] = el.password
    try:
        if d_users[user[0]] == old_psw:  # Проверка на верность старого пароля
            if new_psw == new_psw2:  # Проверка на новый пароль и подтверждение
                items = Item.query.order_by(Item.price).all()
                con = sqlite3.connect('shop.db')
                cur = con.cursor()
                req = f"""UPDATE users SET password = '{new_psw}'
                WHERE email = '{user[0]}'"""
                cur.execute(req)
                con.commit()
                con.close()
                bas.clear()
                return render_template('index.html', data=items, name=user[0], prod={})
            else:
                return "<h1>Новые пароли не совпадают!</h1>"
        else:
            return "<h1>Старый пароль неверный!</h1>"
    except KeyError:
        return "Пользователя с такими данными не существует!"


@app.route('/login', methods=['POST'])  # Авторизация пользователя
def sign_in():
    email_user = request.form['email']
    password_user = request.form['psw']
    d_users = {}
    for el in Users.query.order_by(Users.email).all():
        d_users[el.email] = el.password
    try:
        if d_users[email_user] == password_user:  # проверка логина и пароля
            items = Item.query.order_by(Item.price).all()
            user.append(email_user)
            clear_cart()
            return render_template('index.html', data=items, name=email_user, prod=bas)
        else:
            return "<h1>Вы не зарегистрированы!</h1>"
    except KeyError:
        return "<h1>Пользователя с такими данными не существует!</h1>"


@app.route('/create', methods=['POST', 'GET'])  # Добавление нового товара администратором
def create():
    email_user = request.args.get('email_user')
    file = url_for('static', filename='img/photo.jpg')
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']
        f = request.files['photo']

        with open(f'static/img/{f.filename}', 'wb') as file:
            file.write(f.read())
        file = url_for('static', filename=f'img/{f.filename}')
        item = Item(title=title, price=price, text=text, photo=file)

        try:
            db.session.add(item)
            db.session.commit()
            items = Item.query.order_by(Item.price).all()

            return render_template('index.html', data=items, name=email_user)
        except InvalidRequestError:
            return "Ошибка!"
    else:
        return render_template('create.html', name=email_user)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
