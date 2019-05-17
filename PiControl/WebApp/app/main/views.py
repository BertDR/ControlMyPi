from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
import os
from . import main
from WebApp import db
from WebApp.models import User
from WebApp.app.auth.forms import LoginForm, EditProfileForm
from .forms import ServerInfoForm

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html');

@main.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)

@main.route('/user/<id>', methods=['GET', 'POST'])
@login_required
def user(id):
    if (not current_user.is_admin ) and (str(current_user.id) != id):
        flash('That wasn\'t really your own profile, you requested to change, now was it ?')
        return redirect(url_for('main.user', id=current_user.id))
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
        return redirect(url_for('main.user', id=user.id))
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


@main.route('/user/add', methods=['GET', 'POST'])
@login_required
def adduser():
    if not current_user.is_admin:
        flash('You are no admin...')
        return redirect(url_for('main.users'))
    form = EditProfileForm('Dummy Username')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Please use a different username')
            return redirect(url_for('main.adduser'))
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            flash('Please use a different emailaddress')
            return redirect(url_for('main.adduser'))

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
        return redirect(url_for('main.users', id=user.id))
    return render_template('editprofile.html', title='Edit profile', form=form)

@main.route('/appinit', methods=['GET', 'POST'])
def appinit():
    usercount = User.query.count();
    if usercount > 0 :
        flash('There is an admin user...')
        return redirect(url_for('index'));
    form= EditProfileForm('Admin')
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            about_me=form.about_me.data,
            is_admin=True,
            last_seen=None);
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.users', id=user.id))
    return render_template('editprofile.html', initial_admin = 'YES', form=form)

@main.route('/user/delete/<id>', methods=['GET'])
@login_required
def deleteuser(id):
    if (not current_user.is_admin ) :
        flash('Only admins are allowed to delete.')
        return redirect(url_for('main.users'))
    user = User.query.filter_by(id=id).first_or_404()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('main.users'))

@main.route('/ServerInfo', methods=['GET'])
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


@main.route('/pictures', methods=['GET'])
@login_required
def pictures():
    allpictures = []
    for filename in os.listdir('static/campics/'):
        if filename.endswith("thn.jpg"):
            allpictures.append('static/campics/' + filename)
#             allpictures.append( url_for('static')  + filename)
#            allpictures.append( main.static_url_path  )
        else:
            continue
    allpictures.sort(reverse=True)
    return render_template('pictures.html', title='Pictures', allpictures=allpictures)
