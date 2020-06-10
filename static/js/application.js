$(document).ready(function(){
  let socket = io();
  //let game_state = 'UNKNOWN'
  //$('form#start_game').hide();
  //$('form#end_game').hide();

  socket.on('client initialization', function(msg){
    game_status = msg['game_status'];
    if (game_status == 'ON'){
      $('form#start_game').hide();
    } else if (game_status == 'OFF'){
      $('form#end_game').hide();
    }
  })

  socket.on('game status', function(msg){
    if (msg == 'ON'){
      $('form#start_game').hide();
      $('form#end_game').show();
    } else if (msg == 'OFF'){
      $('form#end_game').hide();
      $('form#start_game').show();
    }
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