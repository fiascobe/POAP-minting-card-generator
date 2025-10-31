import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

def create_cut_line_pdf(output_pdf):
    """
    Generates a PDF with a 3x3 centered grid of rectangular outlines.
    These outlines represent cut lines, inset 3mm from a 57x85mm card size.
    """
    # --- Configuration ---
    # Full card size (including bleed) for layout calculation
    card_width_mm, card_height_mm = 57, 85
    cards_per_row, cards_per_col = 3, 3
    spacing_mm = 5
    bleed_mm = 3

    # --- Convert all millimeter values to PDF points ---
    card_width = card_width_mm * mm
    card_height = card_height_mm * mm
    spacing = spacing_mm * mm
    bleed = bleed_mm * mm
    page_width, page_height = A4

    # Calculate the dimensions of the cut rectangle
    cut_width = (card_width_mm - 2 * bleed_mm) * mm
    cut_height = (card_height_mm - 2 * bleed_mm) * mm

    # --- Centering Logic (based on full card size) ---
    # Calculate total grid dimensions
    grid_width = (cards_per_row * card_width) + ((cards_per_row - 1) * spacing)
    grid_height = (cards_per_col * card_height) + ((cards_per_col - 1) * spacing)

    # Find page center
    center_x = page_width / 2
    center_y = page_height / 2

    # Calculate the bottom-left corner of the *entire grid*
    grid_origin_x = center_x - (grid_width / 2)
    grid_origin_y = center_y - (grid_height / 2)
    # --- End Centering Logic ---

    # --- PDF Creation ---
    c = canvas.Canvas(output_pdf, pagesize=A4)
    cards_per_page = cards_per_row * cards_per_col

    # Set stroke color to black
    c.setStrokeColorRGB(0, 0, 0)
    # Set fill color to none
    c.setFillColorRGB(1, 1, 1, alpha=0) 

    # --- Draw Rectangles on PDF Grid ---
    for i in range(cards_per_page):
        # Determine the row and column for the current card
        row = i // cards_per_row
        col = i % cards_per_row

        # Calculate the bottom-left corner of the *full card* (57x85)
        # We invert the row for bottom-up drawing
        inverted_row = (cards_per_col - 1 - row)
        card_base_x = grid_origin_x + col * (card_width + spacing)
        card_base_y = grid_origin_y + inverted_row * (card_height + spacing)

        # Calculate the bottom-left corner of the *cut rectangle*
        # by adding the 3mm bleed offset.
        cut_rect_x = card_base_x + bleed
        cut_rect_y = card_base_y + bleed

        # Draw the rectangle (outline only)
        c.rect(cut_rect_x, cut_rect_y, cut_width, cut_height, stroke=1, fill=0)

    # --- Finalize PDF ---
    c.save()
    print(f"Successfully generated cut line PDF: {output_pdf}")


if __name__ == "__main__":
    output_pdf_file = 'cut_lines_layout.pdf'
    
    # Call the main function to create the PDF
    create_cut_line_pdf(output_pdf_file)
