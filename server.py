import logging
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
  emit('my response',  {'data': 'Connected'})

@socketio.on('broadcast event')
def broadcast(message):
  emit('my response', {'data': message['data']}, broadcast=True)

if __name__ == '__main__':
  socketio.run(app)