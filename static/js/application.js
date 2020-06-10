// Global variables.
let game_status = 'UNKNOWN'
let player_in_game = false;

let initialize = function(){
  $('form#start_game').hide();
  $('form#end_game').hide();
}

let update_visibilities = function(){
  if (player_in_game){
    $('form#message_sender').hide();
  } else {
    $('form#message_sender').show();
  }
  if (game_status == 'ON'){
    $('form#start_game').hide();
    $('form#end_game').show();
  } else if (game_status == 'OFF'){
    $('form#end_game').hide();
    if (player_in_game){
      $('form#start_game').show();
    } else {
      $('form#start_game').hide();
    }
  }
}

$(document).ready(function(){
  let socket = io();

  initialize();

  socket.on('client initialization', function(msg){
    game_status = msg['game_status'];
    update_visibilities();
  })

  socket.on('game status', function(msg){
    game_status =  msg;
    update_visibilities();
  })

  socket.on('player in game', function(msg){
    player_in_game = msg;
    update_visibilities();
  })

  socket.on('my response', function(msg){
    let players_formatted = '';
    let players_array = msg.players;
    for (index = 0; index < players_array.length; index++){
      let name_i = players_array[index]['name'];
      players_formatted = players_formatted.concat('<br>' + $('<div/>').text(name_i).html());
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

  $('form#message_sender').submit(function(event){
    event.preventDefault();
    socket.emit('add name', {name: $('#player_name').val()});
    $('#player_name').val('');
  })
})