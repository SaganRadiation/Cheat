$(document).ready(function(){
  let socket = io.connect();

  socket.on('connect_response', function(msg){
    $('#log').append('<br>' + $('<div/>').text('Received: ' + msg.data).html());
  })
})