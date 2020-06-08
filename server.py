import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
socketio = SocketIO(app)

@app.route('/')
def hello():
  return render_template('index.html')

@socketio.on('connect')
def connect():
  emit('connect_response',  {'data': 'Connected'})