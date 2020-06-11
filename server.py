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
CARD_SUITS = ('C', 'H', 'D', 'S')
CARD_NUMS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
# Debug flags. These should all be False for real gameplay.
SHOW_DISCARDS = False
TINY_DECK = True

# Game variables
deck = list()
active_player_index = 0
card_sequence = 'UNSET'
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

def increment_card_sequence():
  global card_sequence
  card_sequence_index = CARD_NUMS.index(card_sequence)
  card_sequence_index += 1
  if card_sequence_index == len(CARD_NUMS):
    card_sequence_index = 0
  card_sequence = CARD_NUMS[card_sequence_index]

def get_name(player_id):
  for player in players:
    if player['id'] == player_id:
      return player['name']
  return 'UNKNOWN'

@socketio.on('take turn')
def take_turn(msg):
  cards = msg['cards']
  discard_pile.extend(cards)
  emit('my message', '{} played {} card{}.'.format(get_name(request.sid), len(cards),
    (lambda x: '' if x ==1 else 's')(len(cards))))
  if msg['i_won'] == 'true':
    end_game()
    emit('player win', {'player': get_name(request.sid)}, broadcast=True)
    emit('my message', '{} won the game!'.format(get_name(request.sid)), broadcast=True)
  else:
    increment_player_turn()
    increment_card_sequence()
  emit('my response', {'players': players, 'card_num': card_sequence}, broadcast=True)
  if SHOW_DISCARDS:
    emit('discard pile', {'discard': discard_pile}, broadcast=True)

def get_deck_count(player_count):
  if player_count > 4:
    return 2
  return 1

def initialize_deck(player_count):
  global deck
  deck = []
  if TINY_DECK:
    deck.extend([{'suit': 'S', 'num': 'A'},
                 {'suit': 'C', 'num': 'A'},
                 {'suit': 'D', 'num': 'A'}])
    return
  for _ in range(get_deck_count(player_count)):
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

def deal_out_entire_deck(player_count):
  hands = [[] for _ in range(player_count)]
  for i, card in enumerate(deck):
    hands[i%player_count].append(card)
  deck.clear()
  return hands

def start_game():
  global game_status, card_sequence
  game_status = 'ON'
  card_sequence = 'A'
  start_game_message = 'Starting game.'
  if get_deck_count(len(players)) > 1:
    start_game_message = 'Starting game, using {} decks.'.format(get_deck_count(len(players)))
  emit('my message',  start_game_message, broadcast=True)
  emit('game status', game_status, broadcast=True)
  initialize_deck(len(players))
  global active_player_index
  active_player_index = 0
  hands = deal_out_entire_deck(len(players))
  for i, player in enumerate(players):
    player_id = player['id']
    emit('deal cards', {'cards': hands[i]}, room=player_id)
  annotate_active_player()
  emit('my response', {'players': players, 'card_num': card_sequence}, broadcast=True)

def end_game():
  global game_status
  game_status = 'OFF'
  for i, player in enumerate(players):
    player['active'] = 'false'
  emit('my response', {'players': players}, broadcast=True)
  emit('game status', game_status, broadcast=True)

if __name__ == '__main__':
  socketio.run(app)