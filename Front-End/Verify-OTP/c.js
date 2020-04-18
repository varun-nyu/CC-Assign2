$('button.otp').click(function() {
  var input = $('.otp-input').val();
  getAPIResponse(input)
});

function getAPIResponse(message) {
  fetch('https://6qp8zcn08g.execute-api.us-east-1.amazonaws.com/dev/verify?OTP='+message, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
  .then((res)=>{
    res.json().then((responseObject)=>{
      if (responseObject.status == "unverified") {
        $('body').css('background', 'red');
      } else {
        $('body').css('background', 'green');
      }

      setTimeout(function() {
        $('body').css('background', '#fff');
      }, 1500);
    }).catch((e)=>{
      console.log(e)
    })
})
}