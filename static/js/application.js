$(document).ready(function(){
  let socket = io();

  socket.on('my response', function(msg){
    let messages_formatted = '';
    let message_array = msg.messages;
    for (index = 0; index < message_array.length; index++){
      let message_i = message_array[index];
      messages_formatted = messages_formatted.concat('<br>' + $('<div/>').text(message_i).html());
    }
    $('#log').html(messages_formatted);
  })

  $('form#message_sender').submit(function(event){
    event.preventDefault();
    socket.emit('add message', {data: $('#message_data').val()});
    $('#message_data').val('');
  })
})