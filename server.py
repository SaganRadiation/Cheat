import logging
import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
socketio = SocketIO(app)

sids= []

@app.route('/')
def hello():
  return render_template('index.html')

@socketio.on('connect')
def connect():
  emit('my response',  {'messages': sids})

@socketio.on('add message')
def broadcast(message):
  sids.append(request.sid)
  emit('my response', {'messages': sids}, broadcast=True)

if __name__ == '__main__':
  socketio.run(app)