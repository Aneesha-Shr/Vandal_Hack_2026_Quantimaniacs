from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    # If 'name' isn't in the URL, default to 'World'
    name = request.args.get('name', 'World')
    return 'Hello, ' + name + '!'