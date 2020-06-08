$(document).ready(function(){
  let socket = io.connect();

  socket.on('my response', function(msg){
    $('#log').append('<br>' + $('<div/>').text('Received: ' + msg.data).html());
  })

  $('form#broadcast').submit(function(event){
    event.preventDefault();
    socket.emit('broadcast event', {data: $('#broadcast_data').val()});
  })
})