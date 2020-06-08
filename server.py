import logging
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
socketio = SocketIO(app)

messages = []

@app.route('/')
def hello():
  return render_template('index.html')

@socketio.on('connect')
def connect():
  emit('my response',  {'messages': messages})

@socketio.on('add message')
def broadcast(message):
  messages.append(message['data'])
  emit('my response', {'messages': messages}, broadcast=True)

if __name__ == '__main__':
  socketio.run(app)