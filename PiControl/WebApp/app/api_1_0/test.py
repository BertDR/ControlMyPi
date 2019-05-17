from WebApp.app.api_1_0 import api
from flask import jsonify

# http://127.0.0.1:5000/api/v1.0/posts

@api.route('/posts/')
def get_posts():
    response = jsonify({'name': 'Hello, world!'})
    response.status_code = 200
    return response
