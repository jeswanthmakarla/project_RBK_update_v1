// Generate a random string of 5 characters
function generateRandomString() {
  var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  var string_length = 5;
  var randomString = '';
  for (var i=0; i<string_length; i++) {
    var rnum = Math.floor(Math.random() * chars.length);
    randomString += chars.substring(rnum,rnum+1);
  }
  return randomString;
}

// Draw the CAPTCHA image
function drawCaptcha() {
  var captchaString = generateRandomString();
  var canvas = document.getElementById("captcha");
  var ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = "30px Arial";
  ctx.fillText(captchaString, 10, 35);
  canvas.dataset.captchaString = captchaString;
}

// Validate the CAPTCHA input
function validateCaptcha() {
  var input = document.getElementById("captcha-input").value;
  var captchaString = document.getElementById("captcha").dataset.captchaString;
  var validationMessage = document.getElementById("captcha-validation-message");
  if (input === captchaString) {
    validationMessage.innerHTML = "";
    document.getElementById("login-button").disabled = false;
  } else {
    validationMessage.innerHTML = "Invalid captcha";
    document.getElementById("login-button").disabled = true;
  }
}

// Draw the CAPTCHA on page load
drawCaptcha();

// Validate the CAPTCHA input on keyup
document.getElementById("captcha-input").addEventListener("keyup", validateCaptcha);
