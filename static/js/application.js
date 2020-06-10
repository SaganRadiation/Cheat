// Global variables.
let game_status = 'UNKNOWN'

let initialize = function(){
  $('form#start_game').hide();
  $('form#end_game').hide();
}

let update_visibilities = function(){
  alert('updating visibilities')
  alert(game_status)
  if (game_status == 'ON'){
    $('form#start_game').hide();
    $('form#end_game').show();
  } else if (game_status == 'OFF'){
    $('form#end_game').hide();
    $('form#start_game').show();
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
    alert('switching game status')
    alert(msg)
    game_status =  msg;
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