const year = document.querySelector('#year');
if (year) {
		year.innerHTML = new Date().getFullYear().toString();
}