import logging
import os
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
socketio = SocketIO(app)

## Connection / meta variables
players = []
game_status = 'OFF'

# Game parameters
MINIMUM_PLAYER_COUNT = 1
MAXIMUM_PLAYER_COUNT = 10
NUM_CARDS_TO_DEAL = 1
CARD_SUITS = ('C', 'H', 'D', 'S')
CARD_NUMS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
# Disable this one for real gameplay:
SHOW_DISCARDS = False

# Game variables
deck = list()
active_player_index = 0
discard_pile = list()

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
  players.append({'id': request.sid, 'name': message['name'], 'active': 'false'})
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
      start_game()
    else:
      emit('my message',  "The game is already ON.")
  if message == 'end':
    if game_status == 'ON':
      game_status = 'OFF'
      emit('my message',  "The game is now OFF.", broadcast=True)
      end_game()
    else:
      emit('my message',  "The game is already OFF.")

@socketio.on('end game and kick')
def end_game_and_kick():
  global game_status
  global players
  game_status = 'OFF'
  players = []
  emit('my message',  "The game was ended and all players were kicked.", broadcast=True)
  end_game()


def annotate_active_player():
  for i, player in enumerate(players):
    if i == active_player_index:
      player['active'] = 'true'
    else:
      player['active'] = 'false'

def increment_player_turn():
  global active_player_index
  active_player_index += 1
  if active_player_index == len(players):
    active_player_index = 0
  annotate_active_player()

def get_name(player_id):
  for player in players:
    if player['id'] == player_id:
      return player['name']
  return 'UNKNOWN'

@socketio.on('take turn')
def take_turn(msg):
  cards = msg['cards']
  discard_pile.extend(cards)
  if msg['i_won'] == 'true':
    end_game()
    emit('player win', {'player': get_name(request.sid)}, broadcast=True)
  else:
    increment_player_turn()
  emit('my response', {'players': players}, broadcast=True)
  if SHOW_DISCARDS:
    emit('discard pile', {'discard': discard_pile}, broadcast=True)

def initialize_deck():
  global deck
  deck = []
  for card_suit in reversed(CARD_SUITS):
    for card_num in reversed(CARD_NUMS):
      deck.append({'suit': card_suit, 'num': card_num})
  random.shuffle(deck)

def get_cards_from_deck(n):
  cards_to_return = []
  for _ in range(n):
    if len(deck) == 0:
      return cards_to_return
    cards_to_return.append(deck.pop())
  return cards_to_return

def start_game():
  global game_status
  game_status = 'ON'
  emit('my message',  "Starting game.", broadcast=True)
  emit('game status', game_status, broadcast=True)
  initialize_deck()
  global active_player_index
  active_player_index = 0
  for player in players:
    player_id = player['id']
    cards = get_cards_from_deck(NUM_CARDS_TO_DEAL)
    emit('deal cards', {'cards': cards}, room=player_id)
  annotate_active_player()
  emit('my response', {'players': players}, broadcast=True)

def end_game():
  global game_status
  game_status = 'OFF'
  for i, player in enumerate(players):
    player['active'] = 'false'
  emit('my response', {'players': players}, broadcast=True)
  emit('game status', game_status, broadcast=True)

if __name__ == '__main__':
  socketio.run(app)