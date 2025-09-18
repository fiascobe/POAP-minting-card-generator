# QR Code Card Generator

This Python script automates the process of generating POAP minting cards with individual QR code cards for printing. It takes a list of URLs, creates a unique QR code for each, merges them onto a base card design, and arranges them into a print-ready A4 PDF with crop marks.

## How It Works
The script performs three main steps:
1.  **Generates QR Codes:** Reads URLs from a file named `links.txt` and creates a unique QR code image for each one.
2.  **Merges Images:** Pastes each generated QR code and a corresponding 6-character code onto a `base.png` card design.
3.  **Creates PDF:** Arranges the final card designs onto an A4 PDF page with proper alignment and crop marks, ready for professional printing.

## Getting Started
1.  **Prepare your files:**
    -   **`base.png`**: Your card design image. The script is configured to paste the QR code at a specific position on this image. If you want to design your minting card, it should match exactly the same dimensions and layout from the provided design.
    -   **`links.txt`**: This is where you put your mint links, one URL per line. **You must replace the generic `links.txt` file with your own.**

2.  **Install dependencies:**
    ```bash
    pip install Pillow qrcode reportlab
    ```

3.  **Run the script:**
    ```bash
    python your_script_name.py
    ```
    (Replace `your_script_name.py` with the actual filename of your merged script).

The script will create a `cards_layout.pdf` file in your project folder.