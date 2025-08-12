# Advanced AYSO QR Code Generator

This command-line utility generates a highly customized QR code that points to a specified URL, featuring a visually accurate soccer ball design with a centered logo.

![Example QR Code](AYSO_Homepage_QR_Print_v2.png)
*(Note: You will need to generate this image first to see it here)*

## Features

- **Command-Line Interface:** Easily change the URL, logo, and output file without editing the code.
- **High Error Correction:** Ensures the QR code is scannable even with the logo overlay.
- **Geometrically Accurate Pattern:** Renders a proper truncated icosahedron (soccer ball) pattern.
- **Robust Error Handling:** Provides clear error messages for common issues like missing files.
- **Validation:** Warns you if the logo is too large and might interfere with scanning.

## Prerequisites

- Python 3
- Required libraries: `qrcode` and `pillow`

Install the dependencies using pip:
```bash
pip install qrcode pillow```

## Usage

The script can be run from your terminal.

#### **Basic Usage (uses default settings)**

This will generate the QR code for the AYSO 154 Cypress homepage. Make sure `logo_square.png` is in the same directory.

```bash
python generate_qr.py