// Global variables.
let game_status = 'UNKNOWN'
let player_in_game = 'false';
let player_name = 'Chrysanthemum';
let cards = [];

let initialize = function(){
  $('form#start_game').hide();
  $('form#leave_game').hide();
  $('form#end_game').hide();
}

let update_visibilities = function(){
  if (player_in_game == 'true' && game_status == 'ON'){
    $('form#message_sender').hide();
    $('form#start_game').hide();
    $('form#end_game').show();
    $('#end_game_button').val('End Game');
    $('form#leave_game').hide();
  } else if (player_in_game == 'true' && game_status == 'OFF'){
    $('form#message_sender').hide();
    $('form#start_game').show();
    $('form#end_game').hide();
    $('form#leave_game').show();   
  } else if (player_in_game == 'false' && game_status == 'ON'){
    $('form#message_sender').hide();
    $('form#start_game').hide();
    $('form#end_game').show();
    $('#end_game_button').val('End Game for Other Players (you monster)');
    $('form#leave_game').hide(); 
  } else if (player_in_game == 'false' && game_status == 'OFF'){
    $('form#message_sender').show();
    $('form#start_game').hide();
    $('form#end_game').hide();
    $('form#leave_game').hide();
  } else{
    alert ('invalid state reached in update_visibilities');
  }
}

let update_texts = function(){
   $('#game_status').text(game_status);
   let player_status_text = '';
   if (player_in_game == 'true'){
    player_status_text = 'You are in the game as: ' + player_name
   } else {
    player_status_text = 'You are not in the game.'
   }
  $('#player_status').html(player_status_text);
  if (game_status == 'OFF'){
    $('#list_of_players').text('Players:');
  } else if (game_status == 'ON'){
    $('#list_of_players').text('Players:');
  }
}

let format_card = function(json_card){
  let suit = json_card['suit'];
  let suit_symbol = '';
  if (suit == 'C'){
    suit_symbol = '♧';
  } else if (suit == 'H'){
    suit_symbol = '♥';
  } else if (suit == 'D'){
    suit_symbol = '♢';
  } else if (suit == 'S'){
    suit_symbol = '♤';
  } else {
    alert('attempting to format card with invalid suit: ' + suit);
  }
  return json_card['num'] + suit_symbol;
}

let suit_priority = {
  'S': 0,
  'C': 1,
  'D': 2,
  'H': 3
}

let num_priority = {
  '2': 2,
  '3': 3,
  '4': 4,
  '5': 5,
  '6': 6,
  '7': 7,
  '8': 8,
  '9': 9,
  '10': 10,
  'J': 11,
  'Q': 12,
  'K': 13,
  'A': 14
}

let compare_cards = function(a, b){
  a_suit_priority = suit_priority[a['suit']]
  b_suit_priority = suit_priority[b['suit']]
  a_num_priority = num_priority[a['num']]
  b_num_priority = num_priority[b['num']]
  if (a_num_priority > b_num_priority){
    return 1;
  }
  if (a_num_priority < b_num_priority){
    return -1;
  }
  if (a_suit_priority > b_suit_priority){
    return 1;
  }
  if (a_suit_priority < b_suit_priority){
    return -1;
  }
  alert('compare_cards failure')
  return 0;
}

let sort_cards = function(){
  cards.sort(compare_cards)
}

let show_cards = function(){
  if (cards.length == 0){ 
    return;
  }
  let formatted_cards = cards.map(format_card).join(', ');
  $('#cards').html('Your hand is: ' + formatted_cards + '<br>');
}

let update_visuals = function(){
  update_visibilities();
  update_texts();
  show_cards();
}

$(document).ready(function(){
  let socket = io();

  initialize();

  socket.on('client initialization', function(msg){
    game_status = msg['game_status'];
    update_visuals();
  })

  socket.on('game status', function(msg){
    game_status =  msg;
    update_visuals();
  })

  socket.on('player status', function(msg){
    player_in_game = msg['player_in_game'];
    player_name = msg['name'];
    update_visuals();
  })

  socket.on('deal cards', function(msg){
    cards = msg['cards']
    sort_cards();
    update_visuals();
  })

  socket.on('my response', function(msg){
    let players_formatted = '';
    let players_array = msg.players;
    for (index = 0; index < players_array.length; index++){
      let name_i = players_array[index]['name'];
      let formatted_i = $('<div/>').text(name_i).html();
      if (players_array[index]['active'] == 'true'){
        formatted_i = '<b>' + formatted_i + '</b> ⭠ Active Player'
      }
      players_formatted = players_formatted.concat('<br>' + formatted_i);
    }
    $('#log').html(players_formatted);
  })

  socket.on('my message', function(msg){
    $('#messages').append('<br>' + $('<div/>').text(msg).html());
  })

  $('form#start_game').submit(function(event){
    event.preventDefault();
    socket.emit('game status', 'start'); 
  })

  $('form#end_game').submit(function(event){
    event.preventDefault();
    socket.emit('game status', 'end'); 
  })

  $('form#leave_game').submit(function(event){
    event.preventDefault();
    socket.emit('leave game');
  })

  $('form#message_sender').submit(function(event){
    event.preventDefault();
    socket.emit('add name', {name: $('#player_name').val()});
  })
})