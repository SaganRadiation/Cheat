// Global variables.
let game_status = 'UNKNOWN'
let player_in_game = 'false';

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

let update_visuals = function(){
  update_visibilities();
   $('#game_status').text(game_status);
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

  socket.on('player in game', function(msg){
    player_in_game = msg;
    update_visuals();
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

  $('form#leave_game').submit(function(event){
    event.preventDefault();
    socket.emit('leave game');
  })

  $('form#message_sender').submit(function(event){
    event.preventDefault();
    socket.emit('add name', {name: $('#player_name').val()});
  })
})