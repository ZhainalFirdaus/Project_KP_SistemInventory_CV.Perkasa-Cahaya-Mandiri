from .image_handler import save_picture, delete_old_picture
from .pdf_generator import generate_surat_jalan_pdf

def log_activity(action, details=None):
    from flask_login import current_user
    from ..models import ActivityLog
    from ..extensions import db

    
    if current_user.is_authenticated:
        log = ActivityLog(user_id=current_user.id, action=action, details=details)
        db.session.add(log)
        db.session.commit()

def is_nonsensical(text):
    """
    Mengecek apakah teks terlihat seperti diketik asal (keyboard mashing).
    Return: (bool is_error, str message)
    """
    import re
    t = text.lower().strip()
    
    # 1. Cek karakter berulang (misal: "aaaa")
    if re.search(r'(.)\1{3,}', t):
        return True, "Karakter berulang ditemukan. Mohon masukkan nama yang valid."
        
    # 2. Cek urutan keyboard umum (minimal 5 karakter urut)
    kb_sequences = [
        "asdfghjkl", "qwertyuiop", "zxcvbnm",
        "1234567890", "mnbvcxz", "lkjhgfdsa", "poiuytrewq"
    ]
    for seq in kb_sequences:
        for i in range(len(t) - 4):
            if t[i:i+5] in seq:
                return True, "Input terdeteksi sebagai urutan keyboard."

    # 3. Cek kewajiban huruf vokal (untuk barang dalam bahasa Indonesia/Inggris)
    # Jika panjang > 3 tapi tidak ada vokal (misal: "ghjkl")
    if len(t) > 3 and not re.search(r'[aeiouy]', t):
        return True, "Nama alat harus mengandung setidaknya satu huruf vokal agar valid."

    return False, ""

def generate_qr(data):
    import qrcode
    import io
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer.getvalue()
