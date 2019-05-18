document.getElementById("checkoutButton").onclick = function() {
	document.querySelector('#yourCart').scrollIntoView({ 
  		behavior: 'smooth' 
	});
}

document.getElementById("contactUsButton").onclick = function() {
	document.querySelector('#contactUs').scrollIntoView({ 
  		behavior: 'smooth' 
	});
}

document.getElementById("accountsButton").onclick = function() {
	document.querySelector('#accounts').scrollIntoView({ 
  		behavior: 'smooth' 
	});
}

for (var i = 0; i < document.getElementsByClassName("faqButton").length; i++)
{
	document.getElementsByClassName("faqButton")[i].onclick = function() {
		document.querySelector('#faq').scrollIntoView({ 
  			behavior: 'smooth' 
		});
	}
}


