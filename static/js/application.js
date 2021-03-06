// Global variables.
let game_status = 'UNKNOWN'
let maybe_game_over = 'false';
let player_id = 'unknown';
let player_in_game = 'false';
let player_is_active = 'false';
let first_turn = 'unknown'
let player_name = 'Chrysanthemum';
let players_array = [];
let cards = [];
let discard_pile = [];
let discard_pile_size = -1;
let player_win = 'UNSET';
let card_num = 'UNSET';
let cheatable_action = 'false';

let initialize = function(){
  $('form#start_game').hide();
  $('form#start_game').hide();
  $('form#leave_game').hide();
  $('form#end_game').hide();
  $('#last_action_info').hide();
  $('form#cheater').hide();
}

let populate_card_submission_form = function(){
  let card_submission_html = '';
  for (i = 0; i < cards.length; i++){
    let card = cards[i];
    card_html = '<input type="checkbox" value="' + format_card(card) + 
    '" id="card' + i + '"><label for="card' + i  + '">' + format_card(card) + 
    '</label><br>';
    card_submission_html += card_html;
  }
  $('#cards_to_play').html(card_submission_html);
}

let update_visibilities = function(){
  if (player_in_game == 'true' && cheatable_action=='true'){
    $('form#cheater').show();
  } else{
    $('form#cheater').hide();
  }
  if (player_win == 'true' && player_in_game=='true'){
    $('form#message_sender').hide();
    $('form#start_game').show();
    $('#start_game_button').val('Play Again');
    $('form#end_game').hide();
    $('form#end_game_and_kick').hide();
    $('form#leave_game').show();
    $('form#actions').hide();
    return;
  } 
  if (player_win == 'true' && player_in_game=='false'){
    $('form#message_sender').show();
    $('form#start_game').hide();
    $('form#end_game').hide();
    $('form#end_game_and_kick').hide();
    $('form#leave_game').hide();
    $('form#actions').hide();
    return;
  } 
  $('form#start_game').val('Start Game');
  if (player_in_game == 'true' && game_status == 'ON'){
    $('form#message_sender').hide();
    $('form#start_game').hide();
    $('form#end_game').show();
    $('form#end_game_and_kick').hide();
    $('form#leave_game').hide();
  } else if (player_in_game == 'true' && game_status == 'OFF'){
    $('form#message_sender').hide();
    $('form#start_game').show();
    $('form#end_game').hide();
    $('form#end_game_and_kick').hide();
    $('form#leave_game').show();   
  } else if (player_in_game == 'false' && game_status == 'ON'){
    $('form#message_sender').hide();
    $('form#start_game').hide();
    $('form#end_game').hide();
    $('form#end_game_and_kick').show();
    $('form#leave_game').hide(); 
  } else if (player_in_game == 'false' && game_status == 'OFF'){
    $('form#message_sender').show();
    $('form#start_game').hide();
    $('form#end_game').hide();
    $('form#end_game_and_kick').hide();
    $('form#leave_game').hide();
  } else{
    alert ('invalid state reached in update_visibilities');
  }
  if (player_in_game == 'true' && player_is_active=='true' && maybe_game_over=='false'){
    $('form#actions').show();
    populate_card_submission_form();
  } else {
    $('form#actions').hide();
  }
}

let update_texts = function(){
   $('#game_status').text(game_status);
   $('#card_num').text(card_num);
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
  'A': 1,
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
  return 0;
}

let sort_cards = function(){
  cards.sort(compare_cards)
}

let show_cards = function(){
  if (cards.length == 0){ 
    $('#cards').html('');
    return;
  }
  let formatted_cards = cards.map(format_card).join(', ');
  $('#cards').html('<br><i>Your hand:</i><br>' + formatted_cards + '<br>');
}

let show_player_list = function(){
  let players_formatted = [];
  for (index = 0; index < players_array.length; index++){
    let name_i = players_array[index]['name'];
    let with_cards_i = name_i;
    if (game_status == 'ON'){
      with_cards_i = with_cards_i + ' (' + players_array[index]['card_count'] + ')';
    }
    let formatted_i = $('<div/>').text(with_cards_i).html();
    if (players_array[index]['active'] == 'true' && maybe_game_over == 'false'){
      formatted_i = '<b>' + formatted_i + '</b> ⭠ Card to play: ' + card_num;
    }
    players_formatted.push(formatted_i);
  }
  $('#log').html(players_formatted.join('<br>'));
}

let show_discard_pile = function(){
  if (discard_pile_size == -1){
    $('#discard').html('');
    return;
  }
  let message = '<br><i>Discard pile:</i><br>';
  if (discard_pile.length > 0){
    message = message + discard_pile.join(', ');
  } else{
    message = message + discard_pile_size + ' cards';
  }
  message = message + '<br>';
  $('#discard').html(message);
}

let update_visuals = function(){
  update_visibilities();
  update_texts();
  show_player_list();
  show_cards();
  show_discard_pile();
}

let update_active_player = function(){
  player_is_active = 'false';
  for (index = 0; index < players_array.length; index++){
    if(players_array[index]['id'] == player_id && players_array[index]['active'] == 'true'){
      player_is_active = 'true'; 
    }
  }
}

let set_game_off_values = function(){
  player_is_active = 'false';
  cards = [];
  discard_pile = [];
  discard_pile_size = -1;
  maybe_game_over = 'false';
}

let set_game_start_values = function(){
  player_win = 'false';
  maybe_game_over = 'false';
  discard_pile_size = 0;
}

let remove_cards_from_hand = function(list_of_formatted_cards){
  for (i=0; i < list_of_formatted_cards.length; i++){
    let formatted_card = list_of_formatted_cards[i];
    let matching_idx = cards.findIndex(x => format_card(x) == formatted_card);
    cards.splice(matching_idx, 1);
  }
}

let add_msg_to_log = function(msg){
  msg = msg.replace(/<br>/g,' ');
  $('#messages').prepend($('<div/>').text(msg).text() + '<br>');
}

$(document).ready(function(){
  let socket = io();

  initialize();

  socket.on('connect', function(msg){
    player_id = socket.id
  })

  socket.on('client initialization', function(msg){
    game_status = msg['game_status'];
    update_visuals();
  })

  socket.on('game status', function(msg){
    game_status =  msg;
    if (game_status == 'OFF'){
      set_game_off_values();
    } else{
      set_game_start_values();
    }
    update_visuals();
  })

  socket.on('maybe game over', function(msg){
    maybe_game_over = msg;
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

  socket.on('add extra cards', function(msg){
    cards = cards.concat(msg['cards']);
    sort_cards();
    update_visuals();
  })

  socket.on('discard pile', function(msg){
    if ('discard' in msg){
      discard_pile = msg['discard']
    }
    if ('discard_size' in msg){
      discard_pile_size = msg['discard_size'];
    }
    update_visuals();
  })

  socket.on('my response', function(msg){
    players_array = msg.players;
    if('card_num' in msg){
      card_num = msg['card_num'];
    }
    update_active_player();
    update_visuals();
  })

  socket.on('info message', function(msg){
    add_msg_to_log(msg);
  })

  socket.on('important message', function(msg){
    cheatable_action = 'false';
    update_visibilities();
    $('#last_action_info').show();
    $('#last_action').html(msg)
    add_msg_to_log(msg);
  })

  socket.on('cheatable message', function(msg){
    cheatable_action = 'true';
    update_visibilities();
    $('#last_action_info').show();
    $('#last_action').html(msg)
    add_msg_to_log(msg);
  })

  socket.on('player win', function(msg){
    player_win = 'true';
    update_visuals();
  })

  $('form#start_game').submit(function(event){
    event.preventDefault();
    socket.emit('game status', 'start'); 
  })

  $('form#end_game').submit(function(event){
    event.preventDefault();
    socket.emit('game status', 'end'); 
  })

  $('form#end_game_and_kick').submit(function(event){
    event.preventDefault();
    socket.emit('end game and kick'); 
  })

  $('form#leave_game').submit(function(event){
    event.preventDefault();
    socket.emit('leave game');
  })

  $('form#message_sender').submit(function(event){
    event.preventDefault();
    socket.emit('add name', {name: $('#player_name').val()});
  })

  $('form#actions').submit(function(event){
    event.preventDefault();
    let cards_to_send = [];
    $("#cards_to_play input:checkbox:checked").each(function(index) {
      cards_to_send.push($(this).val());
    });
    remove_cards_from_hand(cards_to_send);
    socket.emit('take turn', {'cards': cards_to_send});
  })

  $('form#cheater').submit(function(event){
    event.preventDefault();
    socket.emit('cheater');
  })
})