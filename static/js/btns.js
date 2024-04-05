var btn1 = document.getElementById("btn1")
btn1.addEventListener('click', (event) =>{
  event.preventDefault()
  btn1.classList.add('reverse')
  btn2.classList.remove('reverse')
  btn3.classList.remove('reverse')
  document.getElementById('form_1').style.display = "block"
  document.getElementById('form_2').style.display = "none"
  document.getElementById('form_3').style.display = "none"
})


var btn2 = document.getElementById("btn2")
btn2.addEventListener('click', (event) =>{
  event.preventDefault()
  btn2.classList.add('reverse')
  btn1.classList.remove('reverse')
  btn3.classList.remove('reverse')
  document.getElementById('form_2').style.display = "block"
  document.getElementById('form_1').style.display = "none"
  document.getElementById('form_3').style.display = "none"
})

var btn3 = document.getElementById("btn3")
btn3.addEventListener('click',(event) =>{
  event.preventDefault()
  btn3.classList.add('reverse')
  btn2.classList.remove('reverse')
  btn1.classList.remove('reverse')
  document.getElementById('form_3').style.display="block"
  document.getElementById('form_2').style.display="none"
  document.getElementById('form_1').style.display="none"

})