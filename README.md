Markdown

# POAP Card Printing Generator

This project provides a set of Python scripts to automatically generate professional, print-ready PDF files for physical POAP (Proof of Attendance Protocol) minting cards. It takes a list of minting URLs, generates unique QR codes, and arranges them onto A4 layouts with corresponding backs and precise cut lines.

## Features

* **Automatic QR Code Generation:** Creates a unique QR code for each URL provided in `links.txt`.
* **Dynamic Card Fronts:** Merges each QR code onto a `front.png` template.
* **Custom Text:** Automatically adds the last 6 characters of the minting link and a sequential counter to each card front.
* **Print-Ready Layout:** Arranges cards in a centered 3x3 grid on an A4 page.
* **Duplex (Two-Sided) Support:** Generates a mirrored 3x3 layout for the card backs (`back.png`) for perfect alignment during two-sided printing.
* **Bleed & Cut Lines:** Creates a separate PDF with precise cut lines, accounting for a 3mm bleed, to guide a professional printer.

## Prerequisites

Before you begin, ensure you have the following installed:

* Python 3.x
* The required Python libraries. You can install them using pip:

```bash
pip install pillow qrcode reportlab
Required Files
Place the following files in the same directory as the Python scripts:

links.txt: A plain text file containing your list of POAP minting URLs. Each URL must be on a new line. (See links.txt for an example).

front.png: The template image for the card front. This image must have a blank area for the QR code.

back.png: The image to be used for the card back.

rubik.ttf: The font file used to write the 6-character code and counter on the card fronts.

How to Use
Follow these steps to generate your print-ready files:

Prepare Your Links: Open the links.txt file and paste your list of minting URLs. Ensure there is only one URL per line.

Run the Scripts: Execute the three Python scripts in order from your terminal.

First, generate the card fronts:

Bash

python "Regular minting card - Front script v2.py"
This will create two new folders (QR Codes and Merged Images) and your main print file: cards_layout_With_Counter_RGB.pdf.

Next, generate the card backs:

Bash

python "Regular minting card - Back script.py"
This creates the mirrored layout for the back: back_layout_rgb.pdf.

Finally, generate the cut lines:

Bash

python "Regular minting card - Cut script.py"
This creates the cutting guide for the printer: cut_lines_layout.pdf.

Send to Printer: You now have three PDF files. Send all three to your print shop.

Printing Instructions
For best results, provide your print shop with the following instructions:

Files to Print:

Front: cards_layout_With_Counter_RGB.pdf

Back: back_layout_rgb.pdf

Cut Guide: cut_lines_layout.pdf

Paper: A4 size, heavy card stock.

Printing:

Print in full color (CMYK).

Print duplex (two-sided), flipping on the long edge.

Ensure printing is set to 100% scale (Actual Size), not "Fit to Page".

Cutting:

Use the cut_lines_layout.pdf as the guide for cutting. The artwork includes a 3mm bleed, so the cuts should be made along these lines.

The final card size after cutting will be 51x79mm (based on a 57x85mm full-bleed design with 3mm bleed).

Customization
You can easily customize the scripts to fit your needs:

Card Size: To change the card size, update the card_width_mm and card_height_mm variables at the top of all three Python scripts.

Layout: You can change the grid by adjusting cards_per_row and cards_per_col in all three scripts.

QR & Text Position: In Regular minting card - Front script v2.py, you can change the paste_position variable for the QR code and the text_x/text_y calculations for the text.

Font: To use a different font, replace rubik.ttf with your own .ttf file and update the font_path variable in Regular minting card - Front script v2.py.