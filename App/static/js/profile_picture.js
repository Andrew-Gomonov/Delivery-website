profile_picture = document.querySelector('#profile_picture')
header_profile_picture = document.querySelector('#header_profile_picture')
if(profile_picture) {
	profile_picture.addEventListener('load', () => {
		let new_photo = document.querySelector('#new_photo');
		// if exists button with id new photo change on this new photo
		if (new_photo) {
			new_photo.addEventListener('change', (event) => {
				let data = event.target;

				if (!FileReader) {
					console.log('FileReader is not supported');
					return;
				}

				if (data.files[0].size === 0) {
					new_photo.value = ''
					alert('Nothing downloaded');
					return;
				}

				let fileReader = new FileReader();
				fileReader.onload = function() {
					profile_picture.src = fileReader.result;
				}

				fileReader.readAsDataURL(data.files[0]);
			});
		}
	});
	profile_picture.addEventListener('error', () => {
		profile_picture.src = "/static/avatars/default.png"
	});
}
header_profile_picture.addEventListener('error', () => {
	header_profile_picture.src = "/static/avatars/default.png"
});
