import atexit
import imghdr
import logging
import os
from hashlib import md5
from flask import current_app
from werkzeug.utils import secure_filename
from App import conn
from App.errors.api import APIBadRequestError


LOG = logging.getLogger(__name__)


def upload_photo(rq, user_id, upload_folder):
    if 'photo' in rq.files:
        # Get the uploaded file
        photo = rq.files['photo']
        filename = secure_filename(rq.files['photo'].filename)
        # Check file name is not empty
        if filename != '':
            # Get the size of the photo
            photo_length = len(photo.read())
            photo.seek(0)
            photo_ext = os.path.splitext(filename)[1]
            # check that the image is the right size for us
            if photo_length < current_app.config['MAX_SIZE_PHOTO']:
                # Checking if a file is an image
                if photo.content_type.startswith('image') \
                        and photo_ext in current_app.config['UPLOAD_EXTENSIONS'] \
                        and photo_ext == validate_image(photo.stream):
                    new_photo_name = md5(str(user_id).encode()).hexdigest()
                    photo.save(os.path.join("App/static/"+upload_folder, new_photo_name))
                    return upload_folder + "/" + new_photo_name
                else:
                    raise APIBadRequestError('Only images are allowed')
            else:
                raise APIBadRequestError('Photo is too large')
        else:
            return upload_folder+"/default.png"
    else:
        raise APIBadRequestError('Where is photo field?')

@atexit.register
def goodbye():
    conn.close()
    LOG.info("Connection to database closed")


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format_image = imghdr.what(None, header)
    if not format_image:
        return None
    return '.' + (format_image if format_image != 'jpeg' else 'jpg')
