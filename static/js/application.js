$(document).ready(function(){
  let socket = io();

  socket.on('my response', function(msg){
    let players_formatted = '';
    let players_array = msg.players;
    for (index = 0; index < players_array.length; index++){
      let name_i = players_array[index]['name'];
      players_formatted = players_formatted.concat('<br>' + $('<div/>').text(name_i).html());
    }
    $('#log').html(players_formatted);
  })

  $('form#message_sender').submit(function(event){
    event.preventDefault();
    socket.emit('add name', {name: $('#player_name').val()});
    $('#player_name').val('');
  })
})