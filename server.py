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
SHOW_DISCARDS = True
TINY_DECK = True
OUT_CHEATERS = True

# Game variables
deck = list()
active_player_index = 0
card_sequence = 'UNSET'
# Discared cards in string format.
discard_pile = list()
# Last cards played in string format.
last_cards_played = list()

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
      emit('info message',  "{} has disconnected".format(player['name']), broadcast=True)
      break

@socketio.on('add name')
def add_player(message):
  if len(players) == MAXIMUM_PLAYER_COUNT :
    emit('important message', 'Sorry, maximum number of players is {}.'.format(MAXIMUM_PLAYER_COUNT))
    return
  if message['name'] == '':
    emit('important message', "Please don't enter a blank name.")
    return
  request_id = request.sid
  for player in players:
    if player['id'] == request_id:
      emit('important message', 'You are already here as ' + player['name'])
      return
  players.append({'id': request.sid, 'name': message['name'], 'active': 'false'})
  emit('my response', {'players': players}, broadcast=True)
  emit('important message', 'You have joined the game.')
  emit('player status', {'player_in_game': 'true', 'name': message['name']})

@socketio.on('leave game')
def leave_game():
  request_id = request.sid
  for player in players:
    if player['id'] == request_id:
      players.remove(player)
      emit('important message', 'You have left the game.')
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
        emit('important message',  '{} players are needed to start.'.format(MINIMUM_PLAYER_COUNT))
        return
      game_status = 'ON'
      start_game()
    else:
      emit('info message',  "The game is already ON.")
  if message == 'end':
    if game_status == 'ON':
      game_status = 'OFF'
      emit('info message',  "The game is now OFF.", broadcast=True)
      end_game()
    else:
      emit('info message',  "The game is already OFF.")

@socketio.on('end game and kick')
def end_game_and_kick():
  global game_status
  global players
  game_status = 'OFF'
  players = []
  emit('important message',  "The game was ended and all players were kicked.", broadcast=True)
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

def get_previous_card_sequence():
  card_sequence_index = CARD_NUMS.index(card_sequence)
  card_sequence_index -= 1
  if card_sequence_index == -1:
    card_sequence_index = len(CARD_NUMS) -1
  return CARD_NUMS[card_sequence_index]

def deformat_card(formatted_card):
  num = formatted_card[:-1]
  formatted_suit = formatted_card[-1]
  deformatted_suit = ''
  if formatted_suit == '♧':
    deformatted_suit = 'C'
  elif formatted_suit == '♥':
    deformatted_suit = 'H'
  elif formatted_suit == '♢':
    deformatted_suit = 'D'
  elif formatted_suit == '♤':
    deformatted_suit = 'S'
  else:
    raise Exception('error deformatting card: {}'.format(formatted_card))
  return {'suit': deformatted_suit, 'num': num}

def get_name(player_id):
  for player in players:
    if player['id'] == player_id:
      return player['name']
  return 'UNKNOWN'

def wordify(n):
  num_map = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine',
             10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen'}
  return num_map.get(n, 'eleventy')

def take_turn_message(player_id, card_count):
  return '{} played {} {}.'.format(
    get_name(request.sid),
    wordify(card_count),
    card_sequence
    )

def is_cheating():
  previous_sequence = get_previous_card_sequence()
  for formatted_card in last_cards_played:
    card = deformat_card(formatted_card)
    if card['num'] != previous_sequence:
      return True
  return False

@socketio.on('take turn')
def take_turn(msg):
  cards = msg['cards']
  discard_pile.extend(cards)
  global last_cards_played
  last_cards_played = cards
  emit('cheatable message', take_turn_message(request.sid, len(cards)), broadcast=True, include_self=False)
  emit('important message', take_turn_message(request.sid, len(cards)))
  if msg['i_won'] == 'true':
    end_game()
    emit('player win', {'player': get_name(request.sid)}, broadcast=True)
    emit('important message', '{} won the game!'.format(get_name(request.sid)), broadcast=True)
  else:
    increment_player_turn()
    increment_card_sequence()
  emit('my response', {'players': players, 'card_num': card_sequence}, broadcast=True)
  if OUT_CHEATERS:
    if is_cheating():
      emit('info message', 'The last player was cheating!!!!', broadcast=True)
    else:
      emit('info message', 'The last player is a saint.', broadcast=True)
  if SHOW_DISCARDS:
    emit('discard pile', {'discard': discard_pile}, broadcast=True)

@socketio.on('cheater')
def cheater():
  emit('important message', '{} called Cheater! They were {}.'.format(
    get_name(request.sid),
    (lambda x: 'right' if x else 'wrong')(is_cheating())))

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
                 {'suit': 'D', 'num': 'A'},
                 {'suit': 'H', 'num': 'A'},
                 {'suit': 'S', 'num': '2'},
                 {'suit': 'C', 'num': '2'}])
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
  emit('important message',  start_game_message, broadcast=True)
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