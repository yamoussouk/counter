//function startTimer(duration, display) {
//    var timer = duration, minutes, seconds;
//    setInterval(function () {
//        minutes = parseInt(timer / 60, 10);
//        seconds = parseInt(timer % 60, 10);
//
//        minutes = minutes < 10 ? "0" + minutes : minutes;
//        seconds = seconds < 10 ? "0" + seconds : seconds;
//
//        display.textContent = minutes + ":" + seconds;
//
//        if (--timer < 0) {
//            timer = duration;
//        }
//    }, 1000);
//}
//
//window.onload = function () {
//    var fiveMinutes = 60 * 99,
//        display = document.querySelector('#time');
//    startTimer(fiveMinutes, display);
//};

var countDownDate = new Date("Dec 5, 2020 19:0:00").getTime();
var x = setInterval(function() {

  // Get today's date and time
  var now = new Date().getTime();

  // Find the distance between now and the count down date
  var distance = countDownDate - now;

  // Time calculations for days, hours, minutes and seconds
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  // Output the result in an element with id="demo"
  document.getElementById("time").innerHTML = days + "d " + hours + "h "
  + minutes + "m " + seconds + "s ";

  // If the count down is over, write some text
  if (distance < 0) {
    clearInterval(x);
    document.getElementById("time").innerHTML = "EXPIRED";
  }
}, 1000);