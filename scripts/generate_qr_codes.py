#!/usr/bin/env python
"""
Generate QR codes for AcademiaPro website
This script creates QR codes for:
1. Website link (to main site)
2. WhatsApp contact
"""

import os
import sys

try:
    import qrcode
except ImportError:
    print("qrcode library not found. Installing...")
    os.system(f"{sys.executable} -m pip install qrcode[pil]")
    import qrcode

from PIL import Image

# Define output directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_dir = os.path.join(project_root, 'app', 'static', 'images')
os.makedirs(img_dir, exist_ok=True)

# QR code data
qr_data = {
    'website-qr': {
        'url': 'https://academiaprolog.com',  # Change to your actual domain
        'filename': 'website-qr.svg'
    },
    'whatsapp-qr': {
        'url': 'https://wa.me/1234567890',  # Change to your WhatsApp number
        'filename': 'whatsapp-qr.svg'
    }
}

def generate_qr_code(data_url, output_path):
    """Generate QR code and save as SVG"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save as PNG first, then convert to SVG
    png_path = output_path.replace('.svg', '.png')
    img.save(png_path)
    print(f"✓ Generated QR code: {png_path}")
    
    return png_path

print("Generating QR codes for AcademiaPro...")

for key, config in qr_data.items():
    output_path = os.path.join(img_dir, config['filename'])
    png_path = generate_qr_code(config['url'], output_path)

print("\nQR codes generated successfully!")
print(f"Location: {img_dir}")
