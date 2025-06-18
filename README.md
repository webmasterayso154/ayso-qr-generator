# Cypress AYSO 154 Soccer Ball QR Code Generator

This is a Python script that generates custom QR codes for the [AYSO Region 154 Cypress](https://www.ayso154cypress.org) website, featuring a soccer ball design with the AYSO logo and red finder patterns. Great for marketing materials, flyers, or registration tables!

![AYSO QR Code Sample](assets/AYSO_Homepage_QR_Print.png)

---

## Features

- **Soccer ball overlay:** Puts the Cypress AYSO 154 logo at the center of a soccer ball, on the QR code.
- **Branded finder patterns:** Red and white corners styled to match AYSO brand colors.
- **High error correction:** Ensures the QR code can be scanned even with the logo overlay.
- **Automatic folder management:** Organizes output and assets for you.
- **Easy customization:** Change URL, colors, logo, or sizing via a single config section.

---

## Project Structure

```
AYSO QR Code/
├── assets/
│   ├── logo_square.png                # Your AYSO logo (square, PNG recommended)
│   └── AYSO_Homepage_QR_Print.png     # Generated QR code output
├── examples/                          # Example outputs (auto-generated)
├── create_qr_3.py                     # Main QR code generator script
├── requirements.txt                   # Python dependency file
├── README.md                          # This file
├── .gitignore
└── venv/                              # (Your virtual environment, not tracked by git)
```

---

## Setup Instructions

### Prerequisites

- Python 3.7 or newer
- pip (Python package manager, included with Python)

### 1. Clone or Download This Repository

```
git clone https://github.com/yourusername/ayso-qr-generator.git
cd ayso-qr-generator
```

### 2. Create and Activate a Virtual Environment (Recommended)

On Windows:
```
python -m venv venv
venv\Scripts\activate
```
On macOS/Linux:
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Add Your Logo

- Place your Cypress AYSO logo as a **square PNG** file named `logo_square.png` in the `assets/` folder.
- If you don't have one, use the sample provided.

---

## Usage

Generate a QR code by running:
```
python create_qr_3.py
```

- The script will create a new QR code with the logo and soccer ball overlay and save it as `assets/AYSO_Homepage_QR_Print.png`.
- It will also save a copy in the `examples/` directory.

---

## Customization

If you want to change the URL, logo, colors, or sizing, edit the `CONFIG` dictionary at the top of `create_qr_3.py`.  
Options include:
- `QR_DATA`: The URL the QR code will point to
- `BOX_SIZE`: Size of QR squares
- `BALL_RELATIVE_SIZE`: Size of soccer ball overlay (% of QR code)
- `LOGO_RELATIVE_SIZE`: Size of logo inside the soccer ball
- Color settings: `NAVY_BLUE`, `VIBRANT_RED`, etc.

---

## Troubleshooting

- **Logo not found:** Make sure `logo_square.png` is in the `assets/` folder or the project root.
- **Import errors:** Make sure you have activated your virtual environment and installed requirements.
- **Output not generated:** Check the terminal for error messages.

---

## Contributing

Pull requests and suggestions welcome! Please create a branch or fork and submit a PR.

---

## Contact

For questions or support, please email WebmasterAYSO154@gmail.com