import os
import uuid
from PIL import Image
from flask import current_app

def save_picture(form_picture):
    """Resizes and compresses image before saving to save storage space."""
    random_hex = uuid.uuid4().hex
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)

    # Image Processing with Pillow
    output_size = (800, 800)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    # Save as JPEG with 85% quality if possible to save space
    if f_ext.lower() in ['.jpg', '.jpeg']:
        i.save(picture_path, optimize=True, quality=85)
    else:
        i.save(picture_path)

    return picture_fn

def delete_old_picture(picture_fn):
    if picture_fn and picture_fn != 'default.jpg':
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
        if os.path.exists(picture_path):
            try:
                os.remove(picture_path)
            except Exception:
                pass
