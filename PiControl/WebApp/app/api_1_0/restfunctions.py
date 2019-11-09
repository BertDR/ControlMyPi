from flask import jsonify, url_for, send_file
from .decorators import permission_required
from . import api
from flask_login import current_user, login_user, logout_user, login_required
from .authentication import unauthorized
import os
import io

# http://127.0.0.1:5000/api/v1.0/posts

@api.route('/posts/')
def get_posts():
    response = jsonify({'name': 'Hello, Bert!'})
    response.status_code = 200
    return response

@api.route('/serverinfo')
def serverinfo():
    from requests import get
    PublicIP = get('https://api.ipify.org').text

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

    try:
        from sense_hat import SenseHat
        sense = SenseHat()
        sense.clear()
        Temperature = sense.get_temperature()
    except:
        Temperature = None
    response = jsonify({
        'PublicIP': PublicIP,
        'PrivateIP': IP,
        'Temperature': Temperature
    })
    response.status_code = 200
    return response


class Picture(object):
    PictureName = ""

    def __init__(self, Name):
        self.PictureName = Name

    def to_json(self):
        json_picture = {
            'url': self.PictureName
        }
        return json_picture


@api.route('/pictures', methods=['GET'])
def pictures():
    allthumbs = []
    allfullpics = []
    allpictureobjects = []
    allfullpictureobjects = []
    for filename in os.listdir(os.path.join(app.root_path, 'campics/')):
        if filename.endswith("thn.jpg"):
            allthumbs.append( url_for ('main.singlepictureraw', filename=filename, _external=True))
        else:
            if filename.endswith(".jpg"):
                allfullpics.append( url_for ('main.singlepictureraw', filename=filename, _external=True))
            else:
                continue
    allthumbs.sort(reverse=True)
    allfullpics.sort(reverse=True)
    for picture in allthumbs:
        allpictureobjects.append(Picture(picture))
    for picture in allfullpics:
        allfullpictureobjects.append(Picture(picture))
    return jsonify({
        'thumbs': [picture.to_json() for picture in allpictureobjects],
        'destinations': [picture.to_json() for picture in allfullpictureobjects]
    })

from flask import send_from_directory
@api.route('/picture/<name>', methods=['GET'])
def picture(name):
    return send_from_directory("campics", name)