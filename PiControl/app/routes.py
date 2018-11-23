from app import app
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.forms import LoginForm, EditProfileForm, ServerInfoForm
from app.models import User
from flask import render_template, flash, redirect, url_for, request
import socket

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html');

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    users = User.query.order_by(User.username).all()
    return render_template('users.html',users=users)

@app.route('/user/<id>', methods=['GET', 'POST'])
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = EditProfileForm(user.username)
    if form.validate_on_submit():
        user.username = form.username.data
        user.about_me = form.about_me.data
        user.email = form.email.data
        if form.password.data != '':
            user.set_password(form.password.data)

        db.session.commit()
        flash ('Your changes have been saved.')
        return redirect(url_for('user', id=user.id))
    elif request.method == 'GET':
        form.username.data = user.username
        form.about_me.data = user.about_me
        form.email.data = user.email
    return render_template('editprofile.html', tile='Edit profile', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('índex'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/ServerInfo', methods=['GET'])
def serverinfo():
    serverinfoform = ServerInfoForm()
    from requests import get

    serverinfoform.PublicIP = get('https://api.ipify.org').text

    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    serverinfoform.PrivateIP = IP;
    return render_template('serverinfo.html',form=serverinfoform)