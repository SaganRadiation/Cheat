$(document).ready(function(){
  let socket = io();

  socket.on('connect_response', function(msg){
    $('log').append('<br>' + $('<div/>').text('Received: ' + msg.data).html());
  })
})