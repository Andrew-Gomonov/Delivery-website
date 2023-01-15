profile_picture = document.querySelector('#profile_picture')
new_photo.onchange = function(event) {
    let data = event.target;

	if (!FileReader) {
		console.log('FileReader is not supported');
		return;
	}

	if (data.files[0].size === 0) {
			photo.value = ''
			alert('Nothing downloaded');
			return;
	}

	var fileReader = new FileReader();
	fileReader.onload = function() {
		profile_picture.src = fileReader.result;
	}

	fileReader.readAsDataURL(data.files[0]);
}