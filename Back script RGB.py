import os
# The 'fitz' library is no longer needed as we are not processing a PDF.
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

def create_back_pdf_layout(back_image_path, output_pdf):
    """
    Arranges a source PNG image onto an A4 PDF in a 3x3 grid,
    mirrored for back-side printing and centered on the page.
    """
    # --- Configuration ---
    card_width_mm, card_height_mm = 57, 85
    cards_per_row, cards_per_col = 3, 3
    # offset_x_mm and offset_y_mm are no longer needed
    spacing_mm = 5

    # --- Convert all millimeter values to PDF points ---
    card_width = card_width_mm * mm
    card_height = card_height_mm * mm
    spacing = spacing_mm * mm
    page_width, page_height = A4

    # --- New Centering Logic ---
    # Calculate total grid dimensions
    grid_width = (cards_per_row * card_width) + ((cards_per_row - 1) * spacing)
    grid_height = (cards_per_col * card_height) + ((cards_per_col - 1) * spacing)

    # Find page center
    center_x = page_width / 2
    center_y = page_height / 2

    # Calculate the bottom-left corner of the *entire grid*
    grid_origin_x = center_x - (grid_width / 2)
    grid_origin_y = center_y - (grid_height / 2)
    # --- End New Logic ---

    # --- Create the new PDF canvas ---
    c = canvas.Canvas(output_pdf, pagesize=A4)
    cards_per_page = cards_per_row * cards_per_col
    
    # --- Place Images on PDF Grid (Mirrored and Centered Layout) ---
    # Loop 9 times to place one image for each spot in the grid
    for i in range(cards_per_page):
        # Determine the row and column for the current card
        row = i // cards_per_row
        col = i % cards_per_row

        # --- COORDINATE CALCULATION (Centered and Mirrored) ---
        
        # Invert column for horizontal mirroring (col 0 becomes 2, 1 remains 1, 2 becomes 0)
        # This places the first column (col=0) at the rightmost grid position.
        inverted_col = (cards_per_row - 1 - col)
        x = grid_origin_x + inverted_col * (card_width + spacing)

        # Invert row for bottom-up Y-axis drawing (row 0 becomes 2, 1 remains 1, 2 becomes 0)
        # This places the first row (row=0) at the topmost grid position.
        inverted_row = (cards_per_col - 1 - row)
        y = grid_origin_y + (inverted_row * (card_height + spacing))
        
        # Draw the source image directly onto the PDF canvas.
        c.drawImage(back_image_path, x, y, width=card_width, height=card_height)

    # --- Finalize PDF ---
    c.save()
    
    print(f"Successfully generated centered back-side PDF: {output_pdf}")


if __name__ == "__main__":
    # Define the input PNG and output PDF filenames.
    back_image_file = 'back.png'  # MODIFIED: Changed from 'back.pdf' to 'back.png'
    output_pdf_file = 'back_layout_rgb.pdf'

    # Check if the required 'back.png' file exists before running.
    if not os.path.exists(back_image_file):
        print(f"Error: The file '{back_image_file}' was not found in this directory.")
        print("Please ensure you have a 'back.png' file in the same folder as the script.")
    else:
        # Call the main function with the image file.
        create_back_pdf_layout(back_image_file, output_pdf_file)
