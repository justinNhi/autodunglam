import jwt
from flask import Flask, request, render_template, session
import netifaces as nif
from datetime import datetime, time, timedelta, date

app = Flask(__name__)
# app.config["SECRET_KEY"] =''
app.secret_key = 'TranDuyLinhDinhGiaXeMienTay7979'


import data_product
import data_user


@app.route('/')
@app.route('/trangchu')
def trangchu():
    return render_template('home_login.html', error_code = -1)


@app.route('/process_user_add', methods=['POST'])
def process_user_add():
    user_name = request.form["user_name"]
    user_password = request.form["user_password"]
    if len(user_name.encode('utf-8')) > len(user_name):
        return render_template('quanlyuser.html', error_code=1)
    else:
        if len(user_name.split(" ")) > 1:
            return render_template('quanlyuser.html', error_code=2)
        else:
            rs = data_user.user_add(user_name=str(user_name), user_password=str(user_password))
            if rs == 1:
                return render_template('quanlyuser.html', error_code=3)
            elif rs == 0:
                return render_template('quanlyuser.html', error_code=0)


@app.route('/user_add_view')
def user_add_view():
    return render_template('quanlyuser.html')


@app.route('/process_home_login', methods=["POST"]) # truyền đường link để theo dõi log
def process_home_login():
    user_name = request.form["user_name"]
    user_password = request.form["user_password"]
    ip_user = request.remote_addr
    browser_name = request.headers.get('User-Agent')
    error_code, group_id, token = data_user.user_login(user_name, user_password, app.secret_key, ip_user, browser_name)
    if error_code == 1:
        return render_template('home_login.html', error_code = error_code)
    elif error_code == 0:
        de_token = jwt.decode(token, app.secret_key, 'HS256')
        session['time_out'] = de_token['TIME_OUT']
        if str(de_token['USER_GROUP_ID']) == str(1):
            return main_menu()
        else:
            render_template('home_login.html', error_code=-1)


@app.route('/main_menu')
def main_menu():
    date_timeout = (date.today()).strftime("%m/%d/%Y")
    time_out = session["time_out"]
    if date_timeout >= time_out:
        return trangchu()
    else:
        return render_template("main_menu.html")







if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
