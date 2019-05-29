from flask import jsonify
from .decorators import permission_required
from . import api
from flask_login import current_user, login_user, logout_user, login_required
from .authentication import unauthorized

# http://127.0.0.1:5000/api/v1.0/posts

@api.route('/posts/')
def get_posts():
    response = jsonify({'name': 'Hello, world!'})
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
    return jsonify({
        'PublicIP': PublicIP,
        'PrivateIP': IP,
        'Temperature': Temperature
    })
