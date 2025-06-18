#!/usr/bin/env python3
"""
Soccer Ball QR Code Generator

This script generates a QR code that points to the AYSO Region 154 Cypress website,
featuring a soccer ball design with the AYSO logo centered inside it.

Features:
- High error correction for better scanning reliability
- Hollow red finder patterns in QR code corners
- Custom soccer ball design with light gray pattern
- Configurable parameters for easy customization
- Extensive error handling and logging

Dependencies:
- qrcode
- pillow (PIL)

Usage:
    python create_qr_3.py

Authors:
    April Henrickson and colleagues
    Last updated: 2025-06-18
"""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageEnhance
import math
import os
import logging
from typing import Tuple, List, Optional

# --- Configure logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('qr_generator')

# --- Configuration Constants ---
# These can be modified to change the behavior of the script
CONFIG = {
    # QR Code settings
    'QR_DATA': "https://www.ayso154cypress.org",
    'BOX_SIZE': 35,       # Size of each QR module in pixels
    'BORDER': 6,          # Quiet zone around QR code
    'OUTER_BORDER': 20,   # Extra white border around the entire image
    
    # File paths
    'LOGO_PATH': "logo_square.png",
    'OUTPUT_PATH': "AYSO_Homepage_QR_Print.png",
    
    # Soccer ball settings
    'BALL_RELATIVE_SIZE': 0.25,   # Soccer ball size relative to QR height
    'LOGO_RELATIVE_SIZE': 0.7,    # Logo size relative to soccer ball size
    
    # Colors (R,G,B)
    'NAVY_BLUE': (0, 0, 102),     # QR code modules
    'VIBRANT_RED': (200, 16, 46), # Finder patterns
    'WHITE': (255, 255, 255),     # Background
    'LIGHT_GRAY': (160, 160, 160) # Soccer ball pattern
}

class QRCodeGenerator:
    """
    Class that handles QR code generation with custom soccer ball design.
    
    This class encapsulates all the functionality to create a QR code with
    a soccer ball logo overlay.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the QR code generator with the provided configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = config
        self.qr = None
        self.qr_img = None
        self.logo = None
        
        # Set up dimensions - will be populated after QR code creation
        self.width = 0
        self.height = 0
        self.soccer_ball_size = 0
    
    def load_logo(self) -> Optional[Image.Image]:
        """
        Load the logo image from the specified file path.
        
        Returns:
            PIL Image object or None if file not found
        """
        logo_path = self.config['LOGO_PATH']
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logger.info(f"Logo loaded successfully: {logo_path}")
            return logo
        except FileNotFoundError:
            logger.error(f"ERROR: The logo file '{logo_path}' was not found.")
            return None
        except Exception as e:
            logger.error(f"Error loading logo: {str(e)}")
            return None
    
    def create_qr_code(self) -> bool:
        """
        Create the base QR code with the configured data.
        
        Returns:
            True if QR code creation was successful, False otherwise
        """
        # Create QR code with maximum error correction
        self.qr = qrcode.QRCode(
            version=None,  # Auto-select optimal version
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Highest error correction
            box_size=self.config['BOX_SIZE'],
            border=self.config['BORDER'],
        )
        
        try:
            self.qr.add_data(self.config['QR_DATA'])
            self.qr.make(fit=True)
            
            # Create base QR image
            self.qr_img = self.qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=SolidFillColorMask(
                    front_color=self.config['NAVY_BLUE'],
                    back_color=self.config['WHITE']
                )
            )
            self.qr_img = self.qr_img.convert("RGBA")
            
            # Store dimensions for later use
            self.width, self.height = self.qr_img.size
            self.soccer_ball_size = int(self.height * self.config['BALL_RELATIVE_SIZE'])
            
            logger.info(f"QR code created with version {self.qr.version}")
            logger.info(f"Using maximum error correction (30% recovery capability)")
            return True
        
        except Exception as e:
            logger.error(f"Error creating QR code: {str(e)}")
            return False
    
    def add_finder_patterns(self) -> None:
        """
        Add custom hollow finder patterns to the QR code corners.
        
        Replaces the standard finder patterns with hollow red squares
        that maintain the correct scanning proportions.
        """
        draw = ImageDraw.Draw(self.qr_img)
        finder_size = 7 * self.qr.box_size  # Standard finder pattern is 7x7 modules
        border_offset = self.qr.border * self.qr.box_size
        
        # Inner function to draw a single finder pattern
        def draw_finder(x: int, y: int) -> None:
            """Draw a single hollow finder pattern at the specified position"""
            # Outer square (red)
            draw.rectangle(
                (x, y, x + finder_size, y + finder_size),
                fill=self.config['VIBRANT_RED']
            )
            
            # Inner square (white)
            inner_pos = self.qr.box_size
            inner_size = finder_size - 2 * inner_pos
            draw.rectangle(
                (x + inner_pos, y + inner_pos, 
                 x + inner_pos + inner_size, y + inner_pos + inner_size),
                fill=self.config['WHITE']
            )
            
            # Center square (red)
            center_pos = 2 * self.qr.box_size
            center_size = 3 * self.qr.box_size
            draw.rectangle(
                (x + center_pos, y + center_pos,
                 x + center_pos + center_size, y + center_pos + center_size),
                fill=self.config['VIBRANT_RED']
            )
        
        # Draw the three finder patterns
        draw_finder(border_offset, border_offset)  # Top-left
        draw_finder(self.width - border_offset - finder_size, border_offset)  # Top-right
        draw_finder(border_offset, self.height - border_offset - finder_size)  # Bottom-left
        
        logger.info("Added custom hollow finder patterns")
    
    def create_soccer_ball(self) -> Image.Image:
        """
        Create a soccer ball image with the logo centered inside.
        
        Returns:
            PIL Image of the soccer ball with logo
        """
        # Create blank canvas for soccer ball
        soccer_ball = Image.new('RGBA', 
                              (self.soccer_ball_size, self.soccer_ball_size), 
                              (0, 0, 0, 0))
        ball_draw = ImageDraw.Draw(soccer_ball)
        
        # Draw white circle as base
        ball_radius = self.soccer_ball_size // 2
        center = ball_radius
        ball_draw.ellipse(
            (0, 0, self.soccer_ball_size-1, self.soccer_ball_size-1), 
            fill=self.config['WHITE']
        )
        
        # Draw soccer ball pattern
        line_width = 1  # Thin lines
        line_color = self.config['LIGHT_GRAY']
        
        # Draw hexagons around the edge to create the classic soccer ball pattern
        # A standard soccer ball has 12 pentagons and 20 hexagons
        for i in range(5):
            # Calculate hexagon positions evenly spaced around the ball
            angle = i * 72  # 360/5 = 72 degrees
            hex_center_x = center + (ball_radius * 0.6) * math.cos(math.radians(angle))
            hex_center_y = center + (ball_radius * 0.6) * math.sin(math.radians(angle))
            
            # Calculate hexagon points
            hexagon_radius = ball_radius * 0.28
            hexagon_points = []
            for j in range(6):
                hex_angle = j * 60  # 360/6 = 60 degrees
                hex_x = hex_center_x + hexagon_radius * math.cos(math.radians(hex_angle))
                hex_y = hex_center_y + hexagon_radius * math.sin(math.radians(hex_angle))
                hexagon_points.append((hex_x, hex_y))
            
            # Draw the hexagon
            if len(hexagon_points) > 2:
                for k in range(len(hexagon_points)):
                    ball_draw.line(
                        (hexagon_points[k], hexagon_points[(k+1) % len(hexagon_points)]),
                        fill=line_color,
                        width=line_width
                    )
        
        # Add a thin border around the soccer ball
        ball_draw.ellipse(
            (1, 1, self.soccer_ball_size-2, self.soccer_ball_size-2), 
            outline=line_color,
            width=line_width
        )
        
        logger.info("Created soccer ball pattern")
        return soccer_ball
    
    def add_logo_to_soccer_ball(self, soccer_ball: Image.Image, logo: Image.Image) -> Image.Image:
        """
        Add the logo to the center of the soccer ball.
        
        Args:
            soccer_ball: The soccer ball image
            logo: The logo image
        
        Returns:
            Soccer ball with centered logo
        """
        # Calculate logo size
        logo_size = int(self.soccer_ball_size * self.config['LOGO_RELATIVE_SIZE'])
        
        # Resize logo while maintaining aspect ratio
        logo_width, logo_height = logo.size
        scale_factor = min(logo_size / logo_width, logo_size / logo_height)
        new_size = (int(logo_width * scale_factor), int(logo_height * scale_factor))
        resized_logo = logo.resize(new_size, Image.LANCZOS)  # High quality resize
        
        # Enhance logo slightly for better visibility
        enhanced_logo = ImageEnhance.Contrast(resized_logo).enhance(1.1)
        
        # Calculate position to center logo on soccer ball
        logo_pos = (
            (self.soccer_ball_size - new_size[0]) // 2,
            (self.soccer_ball_size - new_size[1]) // 2
        )
        
        # Paste logo onto soccer ball
        soccer_ball.paste(enhanced_logo, logo_pos, mask=enhanced_logo)
        
        logger.info(f"Added logo to soccer ball (sized at {logo_size}px)")
        return soccer_ball
    
    def add_soccer_ball_to_qr(self, soccer_ball: Image.Image) -> None:
        """
        Add the soccer ball to the center of the QR code.
        
        Args:
            soccer_ball: The soccer ball image with logo
        """
        # Calculate position to center soccer ball on QR code
        ball_pos = (
            (self.width - self.soccer_ball_size) // 2,
            (self.height - self.soccer_ball_size) // 2
        )
        
        # Calculate how much data is being covered (for diagnosis)
        data_modules_total = (self.qr.version * 4 + 17) ** 2
        quiet_zone_size = self.soccer_ball_size
        quiet_zone_modules = quiet_zone_size / self.qr.box_size
        quiet_zone_area = quiet_zone_modules * quiet_zone_modules
        data_coverage_percent = (quiet_zone_area / data_modules_total) * 100
        
        logger.info(f"Soccer ball covers {data_coverage_percent:.1f}% of QR data area")
        logger.info(f"Note: Values under 25% typically ensure good scanning")
        
        # Paste the soccer ball onto the QR code
        self.qr_img.paste(soccer_ball, ball_pos, mask=soccer_ball)
    
    def add_border_and_save(self) -> bool:
        """
        Add a white border around the QR code and save the final image.
        
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Add final white border
            border_size = self.config['OUTER_BORDER']
            final_img = Image.new(
                'RGBA', 
                (self.width + border_size, self.height + border_size), 
                self.config['WHITE']
            )
            final_img.paste(self.qr_img, (border_size // 2, border_size // 2))
            
            # Save final image
            final_img.save(self.config['OUTPUT_PATH'])
            
            logger.info(f"QR code saved successfully as: {self.config['OUTPUT_PATH']}")
            logger.info(f"It points to: {self.config['QR_DATA']}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving QR code: {str(e)}")
            return False
    
    def generate(self) -> bool:
        """
        Generate the complete QR code with soccer ball and logo.
        
        This is the main method that orchestrates the entire generation process.
        
        Returns:
            True if generation was successful, False otherwise
        """
        # Step 1: Load logo
        logo = self.load_logo()
        if logo is None:
            return False
        
        # Step 2: Create base QR code
        if not self.create_qr_code():
            return False
        
        # Step 3: Add custom finder patterns
        self.add_finder_patterns()
        
        # Step 4: Create soccer ball
        soccer_ball = self.create_soccer_ball()
        
        # Step 5: Add logo to soccer ball
        soccer_ball = self.add_logo_to_soccer_ball(soccer_ball, logo)
        
        # Step 6: Add soccer ball to QR code
        self.add_soccer_ball_to_qr(soccer_ball)
        
        # Step 7: Add border and save final image
        if not self.add_border_and_save():
            return False
        
        logger.info("QR code generation completed successfully")
        logger.info("SCANNING TIPS:")
        logger.info("1. Test with multiple devices and apps")
        logger.info("2. Print at least 1.5 inches (38mm) wide")
        logger.info("3. Use non-glossy paper to reduce glare for outdoor use")
        
        return True


def main() -> None:
    """
    Main function to run the QR code generator.
    
    This serves as the entry point for the script when run directly.
    """
    logger.info("Starting AYSO Soccer Ball QR Code Generator")
    
    # Check if logo file exists before proceeding
    if not os.path.exists(CONFIG['LOGO_PATH']):
        logger.error(f"Logo file not found: {CONFIG['LOGO_PATH']}")
        logger.error("Please place the logo file in the same directory as this script")
        return
    
    # Create and run the generator
    generator = QRCodeGenerator(CONFIG)
    success = generator.generate()
    
    if success:
        logger.info("===== SUCCESS =====")
        logger.info(f"QR code created and saved as {CONFIG['OUTPUT_PATH']}")
        logger.info("Please test scanning thoroughly before printing!")
    else:
        logger.error("QR code generation failed. Check log for details.")


if __name__ == "__main__":
    main()