from flask import render_template, session, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from . import main
from WebApp import db
from WebApp.models import User
from WebApp.models import serverConfig
from WebApp.app.auth.forms import LoginForm, EditProfileForm
from .forms import ServerInfoForm, PicturesForm, ServerConfigForm
from flask import current_app as app
from flask import send_from_directory
from ...Shared import takePicture, deleteSinglePictureShared
import os

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
        return redirect(url_for('main.index'));
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

    serverinfoform.AppRootPath = app.root_path

    return render_template('serverinfo.html', form=serverinfoform)

@main.route('/pictures', methods=['GET'])
@login_required
def pictures():
    pictureform = PicturesForm('Pictures')
    allthumbs = []
    for filename in os.listdir(os.path.join(app.root_path, 'campics/')):
        if filename.endswith("thn.jpg"):
            allthumbs.append('campics/' + filename)
        else:
            continue
    allthumbs.sort(reverse=True)
    return render_template('pictures.html', title='Pictures', allthumbs=allthumbs, form=pictureform)

@main.route('/campics/takepicture', methods=['GET','POST'])
@login_required
def takeCamPicture():
    takePicture()
    return redirect(url_for('main.pictures'))

@main.route('/campics/singlepicture/<path:filename>')
@login_required
def singlepicturefromtemplate(filename):
    return render_template('singlepicture.html', title='Picture ' + filename, destination=filename)

@main.route('/campics/<path:filename>')
@login_required
def singlepictureraw(filename):
    return send_from_directory(
        os.path.join(app.root_path, 'campics'),
        filename
    )

@main.route('/campics/deletesinglepicture/<path>', methods=['POST'])
@login_required
def deletesinglepicture(path):
    deleteSinglePictureShared(path)
    return redirect(url_for('main.pictures'))

@main.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    if (not current_user.is_admin ) :
        flash('You need to be an admin to setup your Pi')
        return redirect(url_for('main.index'))
    ConfigCount = serverConfig.query.count()
    if (ConfigCount < 1):
        MyServerConfig = serverConfig()
        MyServerConfig.id = 1
        MyServerConfig.temperatureDelta = 0
        MyServerConfig.cameraOrientation = 180
        db.session.add (MyServerConfig)
        db.session.commit()
    MyServerConfig = serverConfig.query.filter_by(id=1).first()
    form = ServerConfigForm()
    if form.validate_on_submit():
        MyServerConfig.cameraOrientation = form.cameraOrientation.data
        MyServerConfig.temperatureDelta = form.temperatureDelta.data
        if MyServerConfig.id == 0:
            MyServerConfig.id = 1
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.setup'))
    elif request.method == 'GET':
        form.cameraOrientation.data = MyServerConfig.cameraOrientation
        form.temperatureDelta.data = MyServerConfig.temperatureDelta
    return render_template('serverconfig.html', tile='Edit profile', form=form)

