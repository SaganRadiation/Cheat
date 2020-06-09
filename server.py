import logging
import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
socketio = SocketIO(app)

players = []

@app.route('/')
def hello():
  return render_template('index.html')

@socketio.on('connect')
def connect():
  emit('my response',  {'players': players})

@socketio.on('add name')
def broadcast(message):
  players.append({'id': request.sid, 'name': message['name']})
  emit('my response', {'players': players}, broadcast=True)

if __name__ == '__main__':
  socketio.run(app)