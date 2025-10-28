POAP Minting Card Generator
This project is a collection of Python scripts to generate print-ready PDF files for "Scan to Mint" physical cards. It takes a list of URLs from links.txt, generates a unique QR code for each, and merges it onto a front-card design (front.png).

The scripts then arrange these individual cards into a 3x3 grid, centered on an A4 page, ready for printing. It also includes scripts to generate a corresponding back-side PDF (using back.png) and a separate cut-line guide.

The project provides versions for both RGB (for digital use or standard home printing) and CMYK (for professional press printing), with options to include a sequential counter on each card.

How to Use
Install Dependencies: You'll need to install the required Python libraries.

Bash

pip install Pillow qrcode reportlab
Prepare Input Files:

links.txt: Edit this file and paste in your list of minting URLs, one URL per line.

front.png: This is the design for the front of the card. The script is configured to place the QR code in the blank square.

back.png: Place your card-back design in this file. (Note: The scripts Back script CMYK.py and Back script RGB.py look for back.png. The provided back.jpg will need to be renamed to back.png).


rubik.ttf: The scripts require this font file to be in the same folder to write the 6-character code and counter. If you don't have it, you must download it or change the font_path variable in the scripts to a different .ttf font file.

Run the Scripts (Example): If you want to create professional print-ready files (CMYK) with a counter, you would run the following scripts:

Generate Fronts:

Bash

python "Minting card centered with counter CMYK.py"
This creates cards_layout_with_counter_CMYK.pdf.

Generate Backs:

Bash

python "Back script CMYK.py"
This creates back_layout_CMYK.pdf.

Generate Cut Guide (Optional):

Bash

python "Cut script.py"
This creates cut_lines_layout.pdf.

Print:

Send the generated ...CMYK.pdf files to your print shop.

Instruct them to print double-sided, flipping on the long edge.

The cut_lines_layout.pdf can be used as a reference for cutting.

File Descriptions
Input Files (You provide these)
links.txt

The source list of URLs, one per line. The scripts read this file to generate the QR codes.

front.png

The base image for the front of the card. It should have a transparent or white area for the QR code.

back.jpg / back.png

The base image for the back of the card. Note: All back-side scripts expect this file to be named back.png.

rubik.ttf (Not provided)

A font file required by the scripts to draw text.

Python Scripts (You run these)
Front Card Generation (Choose one)

Minting card centered with counter CMYK.py 

Best for Pro Printing.

Generates QR codes from links.txt.

Merges them onto front.png.

Adds the last 6 characters of the URL as text.

Adds a sequential counter (1, 2, 3...) to each card.

Converts the final images to CMYK (print-ready color space).

Applies a 5% magenta reduction to correct print colors.

Arranges 9 cards on a centered A4 PDF named cards_layout_with_counter_CMYK.pdf.

Minting card centered NO counter CMYK.py

Best for Pro Printing.

Identical to the script above, but does NOT add the sequential counter.

Outputs cards_layout_No_Counter_CMYK.pdf.

Minting card centered with counter RGB.py

For Home Printing / Digital.

Same as the first script, but keeps the images in RGB color space.

Adds a sequential counter.

Outputs cards_layout_With_Counter_RGB.pdf.

Minting card centered without counter RGB.py

For Home Printing / Digital.

Same as the RGB script above, but does NOT add the sequential counter.

Outputs cards_layout_No_counter_RGB.pdf.

Back Card Generation (Choose one)
Back script CMYK.py

Best for Pro Printing.

Takes back.png and converts it to CMYK with magenta reduction.

Arranges it in a 3x3 grid on a centered A4 PDF.

The grid is horizontally mirrored so that when printed double-sided, the backs align perfectly with the fronts.

Outputs back_layout_CMYK.pdf.

Back script RGB.py

For Home Printing / Digital.

Takes back.png and arranges it in a horizontally mirrored 3x3 grid.

Keeps the image in RGB color space.

Outputs back_layout_rgb.pdf.

Utility Script
Cut script.py

Generates a simple PDF with 9 rectangles centered on an A4 page.

These rectangles are inset by 3mm to show the "safe zone" or final cut line for the cards.

Outputs cut_lines_layout.pdf.

Generated Files & Folders (Created by scripts)
QR Codes/ (Folder)

An intermediate folder created by the "Minting card..." scripts. It stores the raw QR code images (e.g., QR_1_111111.png) before they are merged.

Merged Images/ (Folder)

An intermediate folder created by the "Minting card..." scripts. It stores the final, individual card images (e.g., merged_image_1_111111.jpg) after the QR code, text, and counter have been added.

*.pdf (Files)

These are the final, print-ready A4 output files (e.g., cards_layout_with_counter_CMYK.pdf, back_layout_CMYK.pdf).