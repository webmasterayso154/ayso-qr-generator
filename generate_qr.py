#!/usr/bin/env python3
"""
Advanced Soccer Ball QR Code Generator

This script generates a highly customized QR code with a soccer ball design.
It has been refactored for reusability, accuracy, and robustness.

Features:
- Command-line interface for easy customization (URL, logo, output file).
- Geometrically accurate soccer ball pattern (central pentagon + 5 hexagons).
- High error correction for scanning reliability.
- Robust, specific error handling and detailed logging.
- Built-in validation mode to test scannability of the output QR code.

Dependencies:
- qrcode, pillow (PIL)
- pyzbar (for --validate feature)

Usage:
    # Basic usage (uses defaults from CONFIG)
    python generate_qr.py

    # Advanced usage with command-line arguments
    python generate_qr.py --url "https://your.website" --logo "logo.png" --output "custom_qr.png" --validate

Authors:
    April Henrickson and colleagues
    Refactored by a skeptical developer.
    Last updated: 2025-08-11
"""

import argparse
import logging
import math
import os
from typing import Optional, Tuple

import qrcode
from PIL import Image, ImageDraw, ImageEnhance, UnidentifiedImageError
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import SquareModuleDrawer
from qrcode.image.styledpil import StyledPilImage

# --- Configure logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('qr_generator')

# --- Default Configuration Constants ---
# These serve as defaults and can be overridden by command-line arguments.
CONFIG = {
    # QR Code settings
    'QR_DATA': "https://www.ayso154cypress.org",
    'BOX_SIZE': 35,
    'BORDER': 6,
    'OUTER_BORDER': 20,
    
    # File paths
    'LOGO_PATH': "logo_square.png",
    'OUTPUT_PATH': "AYSO_Homepage_QR_Print.png",
    
    # Soccer ball design settings
    'BALL_RELATIVE_SIZE': 0.25,   # Soccer ball size relative to QR height
    'LOGO_RELATIVE_SIZE': 0.7,    # Logo size relative to soccer ball size
    'LOGO_CONTRAST_ENHANCEMENT': 1.1, # Factor to enhance logo contrast
    
    # Geometric factors for the soccer ball pattern
    'PENTAGON_RADIUS_FACTOR': 0.18, # Central pentagon size
    'HEXAGON_RADIUS_FACTOR': 0.16,  # Surrounding hexagons size
    'HEXAGON_DISTANCE_FACTOR': 0.3, # How far hexagons are from the center
    
    # Colors (R,G,B)
    'NAVY_BLUE': (0, 0, 102),
    'VIBRANT_RED': (200, 16, 46),
    'WHITE': (255, 255, 255),
    'LIGHT_GRAY': (160, 160, 160)
}

class QRCodeGenerator:
    """Handles QR code generation with a custom, accurate soccer ball design."""
    
    def __init__(self, config: dict):
        self.config = config
        self.qr = None
        self.qr_img = None
        self.width = 0
        self.height = 0
        self.soccer_ball_size = 0
    
    def load_logo(self) -> Optional[Image.Image]:
        """Loads the logo image from the specified file path."""
        logo_path = self.config['LOGO_PATH']
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logger.info(f"Logo loaded successfully: {logo_path}")
            return logo
        except FileNotFoundError:
            logger.error(f"Logo file not found: '{logo_path}'")
            return None
        except UnidentifiedImageError:
            logger.error(f"Failed to read logo. The file '{logo_path}' may be corrupted or not a valid image.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading the logo: {e}")
            return None
    
    def create_qr_code(self) -> bool:
        """Creates the base QR code."""
        self.qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self.config['BOX_SIZE'],
            border=self.config['BORDER'],
        )
        try:
            self.qr.add_data(self.config['QR_DATA'])
            self.qr.make(fit=True)
            self.qr_img = self.qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=SolidFillColorMask(
                    front_color=self.config['NAVY_BLUE'],
                    back_color=self.config['WHITE']
                )
            ).convert("RGBA")
            self.width, self.height = self.qr_img.size
            self.soccer_ball_size = int(self.height * self.config['BALL_RELATIVE_SIZE'])
            logger.info(f"QR code created with version {self.qr.version} and high error correction.")
            return True
        except Exception as e:
            logger.error(f"Failed to create QR code: {e}")
            return False

    def add_finder_patterns(self) -> None:
        """Adds custom hollow finder patterns to the QR code corners."""
        draw = ImageDraw.Draw(self.qr_img)
        finder_size = 7 * self.qr.box_size
        border_offset = self.qr.border * self.qr.box_size
        
        def draw_finder(x: int, y: int):
            draw.rectangle((x, y, x + finder_size, y + finder_size), fill=self.config['VIBRANT_RED'])
            inner_pos = self.qr.box_size
            inner_size = finder_size - 2 * inner_pos
            draw.rectangle((x + inner_pos, y + inner_pos, x + inner_pos + inner_size, y + inner_pos + inner_size), fill=self.config['WHITE'])
            center_pos = 2 * self.qr.box_size
            center_size = 3 * self.qr.box_size
            draw.rectangle((x + center_pos, y + center_pos, x + center_pos + center_size, y + center_pos + center_size), fill=self.config['VIBRANT_RED'])
        
        positions = [
            (border_offset, border_offset),
            (self.width - border_offset - finder_size, border_offset),
            (border_offset, self.height - border_offset - finder_size)
        ]
        for x, y in positions:
            draw_finder(x, y)
        logger.info("Added custom hollow finder patterns.")
    
    def _draw_polygon(self, draw: ImageDraw.Draw, center: Tuple[float, float], radius: float, sides: int, rotation: float, color: Tuple[int, int, int], width: int):
        """Helper function to draw a regular polygon."""
        points = []
        for i in range(sides):
            angle = math.radians((i * 360 / sides) + rotation)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        draw.polygon(points, outline=color, width=width)

    def _create_soccer_ball_pattern(self) -> Image.Image:
        """Creates a geometrically accurate 2D soccer ball pattern."""
        soccer_ball = Image.new('RGBA', (self.soccer_ball_size, self.soccer_ball_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(soccer_ball)
        center_xy = self.soccer_ball_size / 2
        ball_radius = center_xy
        
        # Base white circle
        draw.ellipse((0, 0, self.soccer_ball_size-1, self.soccer_ball_size-1), fill=self.config['WHITE'])
        
        # Draw pattern
        line_color = self.config['LIGHT_GRAY']
        line_width = max(1, int(self.soccer_ball_size / 200)) # Scale line width
        
        # Central Pentagon
        pent_radius = ball_radius * self.config['PENTAGON_RADIUS_FACTOR']
        self._draw_polygon(draw, (center_xy, center_xy), pent_radius, 5, -90, line_color, line_width)
        
        # Surrounding Hexagons
        hex_radius = ball_radius * self.config['HEXAGON_RADIUS_FACTOR']
        hex_dist = ball_radius * self.config['HEXAGON_DISTANCE_FACTOR']
        for i in range(5):
            angle = math.radians(i * 72) # 360/5
            hex_center_x = center_xy + hex_dist * math.cos(angle)
            hex_center_y = center_xy + hex_dist * math.sin(angle)
            self._draw_polygon(draw, (hex_center_x, hex_center_y), hex_radius, 6, 0, line_color, line_width)
            
        # Thin border around the ball
        draw.ellipse((0, 0, self.soccer_ball_size-1, self.soccer_ball_size-1), outline=line_color, width=line_width)
        
        logger.info("Created geometrically accurate soccer ball pattern.")
        return soccer_ball

    def add_logo_to_ball(self, soccer_ball: Image.Image, logo: Image.Image) -> Image.Image:
        """Adds and enhances the logo to the center of the ball image."""
        logo_size = int(self.soccer_ball_size * self.config['LOGO_RELATIVE_SIZE'])
        resized_logo = logo.copy()
        resized_logo.thumbnail((logo_size, logo_size), Image.LANCZOS)
        
        enhancer = ImageEnhance.Contrast(resized_logo)
        enhanced_logo = enhancer.enhance(self.config['LOGO_CONTRAST_ENHANCEMENT'])
        
        logo_pos = ((self.soccer_ball_size - resized_logo.width) // 2, (self.soccer_ball_size - resized_logo.height) // 2)
        soccer_ball.paste(enhanced_logo, logo_pos, mask=enhanced_logo)
        logger.info(f"Pasted logo onto soccer ball.")
        return soccer_ball

    def add_ball_to_qr(self, soccer_ball_with_logo: Image.Image) -> None:
        """Adds the final ball image to the QR code center."""
        ball_pos = ((self.width - self.soccer_ball_size) // 2, (self.height - self.soccer_ball_size) // 2)
        
        coverage = (self.soccer_ball_size ** 2) / (self.width * self.height) * 100
        logger.info(f"Soccer ball overlay covers ~{coverage:.1f}% of the QR code image area.")
        if coverage > 25:
            logger.warning("Coverage exceeds 25%. QR code may be difficult to scan. Consider reducing BALL_RELATIVE_SIZE.")
            
        self.qr_img.paste(soccer_ball_with_logo, ball_pos, mask=soccer_ball_with_logo)

    def save_final_image(self) -> bool:
        """Adds a final border and saves the image to disk."""
        border_size = self.config['OUTER_BORDER']
        final_img = Image.new('RGBA', (self.width + border_size, self.height + border_size), self.config['WHITE'])
        final_img.paste(self.qr_img, (border_size // 2, border_size // 2))
        
        output_path = self.config['OUTPUT_PATH']
        try:
            final_img.save(output_path)
            logger.info(f"QR code saved successfully to: {output_path}")
            return True
        except PermissionError:
            logger.error(f"Permission denied. Could not save file to '{output_path}'.")
            return False
        except IOError as e:
            logger.error(f"Failed to save image to '{output_path}'. An I/O error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during file saving: {e}")
            return False
            
    def generate(self) -> bool:
        """Orchestrates the entire QR code generation process."""
        logo = self.load_logo()
        if logo is None: return False
        
        if not self.create_qr_code(): return False
        
        self.add_finder_patterns()
        
        soccer_ball_pattern = self._create_soccer_ball_pattern()
        soccer_ball_with_logo = self.add_logo_to_ball(soccer_ball_pattern, logo)
        
        self.add_ball_to_qr(soccer_ball_with_logo)
        
        if not self.save_final_image(): return False
        
        logger.info("QR code generation complete.")
        return True

def validate_qr_code(image_path: str, expected_data: str) -> bool:
    """Uses pyzbar to validate the generated QR code."""
    try:
        from pyzbar.pyzbar import decode
    except ImportError:
        logger.warning("pyzbar not installed. Skipping validation. To enable, run: pip install pyzbar")
        return True # Cannot validate, so don't fail

    logger.info(f"--- Running Validation on {image_path} ---")
    try:
        image = Image.open(image_path)
        decoded_objects = decode(image)
        if not decoded_objects:
            logger.error("VALIDATION FAILED: No QR code found in the generated image.")
            return False
        
        for obj in decoded_objects:
            decoded_data = obj.data.decode('utf-8')
            if decoded_data == expected_data:
                logger.info(f"VALIDATION SUCCESS: Found QR code with matching data: {decoded_data}")
                return True
        
        logger.error(f"VALIDATION FAILED: Found a QR code, but data does not match.")
        logger.error(f"  Expected: {expected_data}")
        logger.error(f"  Found:    {decoded_objects[0].data.decode('utf-8')}")
        return False

    except Exception as e:
        logger.error(f"An error occurred during validation: {e}")
        return False

def main() -> None:
    """Main function to parse arguments and run the generator."""
    parser = argparse.ArgumentParser(
        description="Advanced Soccer Ball QR Code Generator.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--url", type=str, help="URL for the QR code to point to.")
    parser.add_argument("--logo_path", type=str, help="File path for the logo image.")
    parser.add_argument("--output_path", type=str, help="File path to save the final QR code.")
    parser.add_argument("--validate", action="store_true", help="Validate the generated QR code by reading it back.\nRequires 'pyzbar' library: pip install pyzbar")
    args = parser.parse_args()

    # Update config with any provided command-line arguments
    cli_config = CONFIG.copy()
    if args.url: cli_config['QR_DATA'] = args.url
    if args.logo_path: cli_config['LOGO_PATH'] = args.logo_path
    if args.output_path: cli_config['OUTPUT_PATH'] = args.output_path

    logger.info("Starting AYSO Soccer Ball QR Code Generator...")
    if not os.path.exists(cli_config['LOGO_PATH']):
        logger.error(f"Logo file '{cli_config['LOGO_PATH']}' not found. Please specify a valid path with --logo_path.")
        return

    generator = QRCodeGenerator(cli_config)
    success = generator.generate()
    
    if success:
        logger.info("===== Generation Successful =====")
        if args.validate:
            validation_success = validate_qr_code(cli_config['OUTPUT_PATH'], cli_config['QR_DATA'])
            if not validation_success:
                logger.error("Please check parameters. The QR code might be too obscured.")
    else:
        logger.error("===== Generation Failed =====")
        logger.error("QR code generation failed. Please check the log for details.")

if __name__ == "__main__":
    main()```