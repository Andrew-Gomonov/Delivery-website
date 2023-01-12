import imghdr


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format_image = imghdr.what(None, header)
    if not format_image:
        return None
    return '.' + (format_image if format_image != 'jpeg' else 'jpg')
