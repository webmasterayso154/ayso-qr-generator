#!/usr/bin/env python3
import os
import shutil
import logging
import math
from pathlib import Path

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageEnhance

CONFIG = {
    'QR_DATA': "https://www.ayso154cypress.org",
    'BOX_SIZE': 35,
    'BORDER': 6,
    'OUTER_BORDER': 20,
    'LOGO_PATH': "assets/logo_square.png",
    'LOGO_SOURCE': "logo_square.png",
    'OUTPUT_PATH': "assets/AYSO_Homepage_QR_Print.png",
    'ASSETS_DIR': "assets",
    'EXAMPLES_DIR': "examples",
    'BALL_RELATIVE_SIZE': 0.25,
    'LOGO_RELATIVE_SIZE': 0.7,
    'NAVY_BLUE': (0, 0, 102),
    'VIBRANT_RED': (200, 16, 46),
    'WHITE': (255, 255, 255),
    'LIGHT_GRAY': (160, 160, 160)
}

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ayso_qr")

def ensure_directories():
    for dir_path in [CONFIG['ASSETS_DIR'], CONFIG['EXAMPLES_DIR']]:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Checked/created directory: {dir_path}")

def ensure_logo_in_assets():
    logo_in_assets = Path(CONFIG['LOGO_PATH'])
    logo_in_root = Path(CONFIG['LOGO_SOURCE'])
    if logo_in_assets.is_file():
        logger.info(f"Logo found in assets: {logo_in_assets}")
        return True
    elif logo_in_root.is_file():
        shutil.move(str(logo_in_root), str(logo_in_assets))
        logger.info(f"Moved logo from root to assets: {logo_in_assets}")
        return True
    else:
        logger.error(
            f"Logo file not found! Please add your logo as '{CONFIG['LOGO_PATH']}' or '{CONFIG['LOGO_SOURCE']}'."
        )
        return False

def create_qr_code():
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=CONFIG['BOX_SIZE'],
        border=CONFIG['BORDER'],
    )
    qr.add_data(CONFIG['QR_DATA'])
    qr.make(fit=True)
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=SquareModuleDrawer(),
        color_mask=SolidFillColorMask(
            front_color=CONFIG['NAVY_BLUE'], back_color=CONFIG['WHITE']
        ),
    ).convert("RGBA")
    logger.info("QR code generated")
    return qr_img, qr

def add_finder_patterns(qr_img, qr):
    draw = ImageDraw.Draw(qr_img)
    finder_size = 7 * qr.box_size
    border_offset = qr.border * qr.box_size
    def draw_finder(x, y):
        draw.rectangle((x, y, x + finder_size, y + finder_size), fill=CONFIG['VIBRANT_RED'])
        inner = qr.box_size
        inner_size = finder_size - 2 * inner
        draw.rectangle((x + inner, y + inner, x + inner + inner_size, y + inner + inner_size), fill=CONFIG['WHITE'])
        center = 2 * qr.box_size
        center_size = 3 * qr.box_size
        draw.rectangle((x + center, y + center, x + center + center_size, y + center + center_size), fill=CONFIG['VIBRANT_RED'])
    draw_finder(border_offset, border_offset)
    draw_finder(qr_img.width - border_offset - finder_size, border_offset)
    draw_finder(border_offset, qr_img.height - border_offset - finder_size)
    logger.info("Custom finder patterns added")

def create_soccer_ball_with_logo(qr_img, logo_img):
    qr_w, qr_h = qr_img.size
    ball_size = int(qr_h * CONFIG['BALL_RELATIVE_SIZE'])
    soccer_ball = Image.new('RGBA', (ball_size, ball_size), (0,0,0,0))
    ball_draw = ImageDraw.Draw(soccer_ball)
    ball_radius = ball_size // 2
    center = ball_radius
    ball_draw.ellipse((0, 0, ball_size-1, ball_size-1), fill=CONFIG['WHITE'])
    line_width = 1
    line_color = CONFIG['LIGHT_GRAY']
    for i in range(5):
        angle = i * 72
        hex_cx = center + (ball_radius * 0.6) * math.cos(math.radians(angle))
        hex_cy = center + (ball_radius * 0.6) * math.sin(math.radians(angle))
        hex_r = ball_radius * 0.28
        hex_pts = []
        for j in range(6):
            hex_angle = j * 60
            hx = hex_cx + hex_r * math.cos(math.radians(hex_angle))
            hy = hex_cy + hex_r * math.sin(math.radians(hex_angle))
            hex_pts.append((hx, hy))
        if len(hex_pts) > 2:
            for k in range(len(hex_pts)):
                ball_draw.line((hex_pts[k], hex_pts[(k+1)%len(hex_pts)]), fill=line_color, width=line_width)
    ball_draw.ellipse((1, 1, ball_size-2, ball_size-2), outline=line_color, width=line_width)
    logo_size = int(ball_size * CONFIG['LOGO_RELATIVE_SIZE'])
    lw, lh = logo_img.size
    scale = min(logo_size / lw, logo_size / lh)
    new_size = (int(lw * scale), int(lh * scale))
    resized_logo = logo_img.resize(new_size, Image.LANCZOS)
    enhanced_logo = ImageEnhance.Contrast(resized_logo).enhance(1.1)
    logo_pos = ((ball_size - enhanced_logo.width) // 2, (ball_size - enhanced_logo.height) // 2)
    soccer_ball.paste(enhanced_logo, logo_pos, mask=enhanced_logo)
    ball_pos = ((qr_w - ball_size) // 2, (qr_h - ball_size) // 2)
    qr_img.paste(soccer_ball, ball_pos, mask=soccer_ball)
    logger.info("Soccer ball with logo overlaid on QR code")
    return qr_img

def save_with_border(qr_img):
    border = CONFIG['OUTER_BORDER']
    final_img = Image.new('RGBA', (qr_img.width + border, qr_img.height + border), CONFIG['WHITE'])
    final_img.paste(qr_img, (border // 2, border // 2))
    final_img.save(CONFIG['OUTPUT_PATH'])
    logger.info(f"Saved QR code as: {CONFIG['OUTPUT_PATH']}")
    example_path = f"examples/QR_Example_{qr_img.width}x{qr_img.height}.png"
    final_img.save(example_path)
    logger.info(f"Saved example copy as: {example_path}")

def main():
    ensure_directories()
    if not ensure_logo_in_assets():
        return
    try:
        logo_img = Image.open(CONFIG['LOGO_PATH']).convert('RGBA')
    except Exception as e:
        logger.error(f"Could not open logo: {e}")
        return
    qr_img, qr = create_qr_code()
    add_finder_patterns(qr_img, qr)
    qr_img = create_soccer_ball_with_logo(qr_img, logo_img)
    save_with_border(qr_img)
    logger.info("QR code generation complete. Test the output with multiple QR apps and devices!")

if __name__ == "__main__":
    main()