import logging
import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
socketio = SocketIO(app)

players = []
game_status = 'OFF'
MINIMUM_PLAYER_COUNT = 2
MAXIMUM_PLAYER_COUNT = 10

@app.route('/')
def hello():
  return render_template('index.html')

@socketio.on('connect')
def connect():
  emit('client initialization', {'game_status': game_status})
  emit('my response',  {'players': players})

@socketio.on('disconnect')
def disconnect():
  request_id = request.sid
  disconnected_player = False
  for player in players:
    if player['id'] == request_id:
      disconnected_player = True
      players.remove(player)
      emit('my message',  "{} has disconnected".format(player['name']), broadcast=True)
      break
  if disconnected_player == False:
    emit('my message',  "No player {} to disconnect. This should never happen.".format(request_id), broadcast=True)

@socketio.on('add name')
def add_player(message):
  if len(players) == MAXIMUM_PLAYER_COUNT :
    emit('my message', 'Sorry, maximum number of players is {}.'.format(MAXIMUM_PLAYER_COUNT))
    return
  if message['name'] == '':
    emit('my message', "Please don't enter a blank name.")
    return
  request_id = request.sid
  for player in players:
    if player['id'] == request_id:
      emit('my message', 'You are already here as ' + player['name'])
      return
  players.append({'id': request.sid, 'name': message['name']})
  emit('my response', {'players': players}, broadcast=True)
  emit('my message', 'You have joined the game.')
  emit('player status', {'player_in_game': 'true', 'name': message['name']})

@socketio.on('leave game')
def leave_game():
  request_id = request.sid
  for player in players:
    if player['id'] == request_id:
      players.remove(player)
      emit('my message', 'You have left the game.')
      emit('player status', {'player_in_game': 'false', 'name': 'none'})
      emit('my response', {'players': players}, broadcast=True)
      return
  emit('my response', 'You are not here. This should never happen.')

@socketio.on('game status')
def change_game_status(message):
  global game_status
  if message == 'start':
    if game_status == 'OFF':
      if len(players) < MINIMUM_PLAYER_COUNT :
        emit('my message',  '{} players are needed to start.'.format(MINIMUM_PLAYER_COUNT))
        return
      game_status = 'ON'
      emit('my message',  "The game is now ON.", broadcast=True)
      emit('game status', game_status, broadcast=True)
      start_game()
    else:
      emit('my message',  "The game is already ON.")
  if message == 'end':
    if game_status == 'ON':
      game_status = 'OFF'
      emit('my message',  "The game is now OFF.", broadcast=True)
      emit('game status', game_status, broadcast=True)
    else:
      emit('my message',  "The game is already OFF.")

def start_game():
  emit('my message',  "Starting game.", broadcast=True)
  for i, player in enumerate(players):
    player_id = player['id']
    if i == 0:
      cards = [{'suit': 'C', 'num': 5}, {'suit': 'C', 'num': 6}, {'suit': 'H', 'num': 7}]
    else:
      cards = [{'suit': 'D', 'num': 4}, {'suit': 'D', 'num': 2}, {'suit': 'D', 'num': 3}]
    emit('deal cards', {'cards': cards}, room=player_id)

if __name__ == '__main__':
  socketio.run(app)