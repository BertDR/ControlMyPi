from app import app
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app import LoginForm, EditProfileForm, ServerInfoForm
from app import User
from flask import render_template, flash, redirect, url_for, request
import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html');


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)


@app.route('/user/<id>', methods=['GET', 'POST'])
@login_required
def user(id):
    if (not current_user.is_admin ) and (str(current_user.id) != id):
        flash('That wasn\'t really your own profile, you requested to change, now was it ?')
        return redirect(url_for('user', id=current_user.id))
    user = User.query.filter_by(id=id).first_or_404()
    form = EditProfileForm(user.username)
    if form.validate_on_submit():
        user.username = form.username.data
        user.about_me = form.about_me.data
        user.email = form.email.data
        if current_user.is_admin:
            user.is_admin = request.form.get('is_admin') == 'y'
        if form.password.data != '':
            user.set_password(form.password.data)

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', id=user.id))
    elif request.method == 'GET':
        if current_user.is_admin:
            flash('You are admin')
        form.username.data = user.username
        form.about_me.data = user.about_me
        form.email.data = user.email
        if user.is_admin:
            form.is_admin.data = True
        else:
            form.is_admin.data = False
    return render_template('editprofile.html', tile='Edit profile', form=form)


@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def adduser():
    if not current_user.is_admin:
        flash('You are no admin...')
        return redirect(url_for('users'))
    form = EditProfileForm('Dummy Username')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Please use a different username')
            return redirect(url_for('adduser'))
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            flash('Please use a different emailaddress')
            return redirect(url_for('adduser'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            about_me=form.about_me.data,
            is_admin=form.is_admin.data,
            last_seen=None);
        user.set_password(form.password.data);
        db.session.add(user)
        db.session.commit()
##        user.is_admin = request.form.get ('is_admin') == 'y'
        flash('Your changes have been saved.')
        return redirect(url_for('users', id=user.id))
    return render_template('editprofile.html', tile='Edit profile', form=form)

@app.route('/user/delete/<id>', methods=['GET'])
@login_required
def deleteuser(id):
    if (not current_user.is_admin ) :
        flash('Only admins are allowed to delete.')
        return redirect(url_for('users'))
    user = User.query.filter_by(id=id).first_or_404()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('users'))

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
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/ServerInfo', methods=['GET'])
@login_required
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

    try:
        from sense_hat import SenseHat
        sense = SenseHat()
        sense.clear()
        serverinfoform.Temperature = sense.get_temperature()
    except:
        serverinfoform.Temperature = None

    return render_template('serverinfo.html', form=serverinfoform)


@app.route('/pictures', methods=['GET'])
@login_required
def pictures():
    allpictures = []
    for filename in os.listdir('app/static/campics/'):
        if filename.endswith("thn.jpg"):
            allpictures.append('/static/campics/' + filename)
        else:
            continue
    allpictures.sort(reverse=True)
    return render_template('pictures.html', title='Pictures', allpictures=allpictures)
