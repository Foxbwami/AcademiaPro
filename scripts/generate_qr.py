import qrcode
from PIL import Image
import os

OUT_DIR = os.path.join('app', 'static', 'images')
os.makedirs(OUT_DIR, exist_ok=True)

def make_qr(data, path, size=400):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img = img.resize((size, size), Image.NEAREST)
    img.save(path)

if __name__ == '__main__':
    whatsapp_url = 'https://wa.me/447426105606'
    website_url = 'http://127.0.0.1:5000/'

    make_qr(whatsapp_url, os.path.join(OUT_DIR, 'whatsapp-qr.png'), 400)
    make_qr(website_url, os.path.join(OUT_DIR, 'website-qr.png'), 400)
    print('Generated whatsapp-qr.png and website-qr.png in', OUT_DIR)
