import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader  # To read the PIL image
from PIL import Image                      # For image conversion

def create_back_pdf_layout(back_image_path, output_pdf):
    """
    Arranges a source PNG image onto an A4 PDF in a 3x3 grid,
    mirrored for back-side printing, centered, and in CMYK color space
    with a manual magenta reduction.
    """
    # --- Configuration ---
    card_width_mm, card_height_mm = 57, 85
    cards_per_row, cards_per_col = 3, 3
    spacing_mm = 5

    # --- Convert all millimeter values to PDF points ---
    card_width = card_width_mm * mm
    card_height = card_height_mm * mm
    spacing = spacing_mm * mm
    page_width, page_height = A4

    # --- New Centering Logic ---
    grid_width = (cards_per_row * card_width) + ((cards_per_row - 1) * spacing)
    grid_height = (cards_per_col * card_height) + ((cards_per_col - 1) * spacing)
    center_x = page_width / 2
    center_y = page_height / 2
    grid_origin_x = center_x - (grid_width / 2)
    grid_origin_y = center_y - (grid_height / 2)
    # --- End New Logic ---

    # --- Create the new PDF canvas ---
    c = canvas.Canvas(output_pdf, pagesize=A4) 
    cards_per_page = cards_per_row * cards_per_col
    
    # --- Load and Convert Image to CMYK ---
    try:
        print(f"Loading '{back_image_path}' and converting to CMYK...")
        # Open the source image (which is RGB)
        pil_image_rgb = Image.open(back_image_path)
        
        # Convert the image to CMYK mode
        pil_image_cmyk = pil_image_rgb.convert('CMYK')
        
        # --- START FIX: Manually reduce Magenta (User Request) ---
        # This is a 'brute-force' adjustment.
        # 0.95 = 5% reduction
        # 0.90 = 10% reduction
        # Start with a small value and adjust as needed.
        magenta_factor = 0.95 # <-- ADJUST THIS VALUE AS NEEDED

        try:
            # Split the image into its 4 CMYK channels
            c_chan, m_chan, y_chan, k_chan = pil_image_cmyk.split()

            # Apply the reduction to the Magenta channel
            # .point() applies a function to every pixel in that channel
            m_chan = m_chan.point(lambda i: int(i * magenta_factor))

            # Re-merge the channels back into a single CMYK image
            pil_image_cmyk = Image.merge("CMYK", (c_chan, m_chan, y_chan, k_chan))
            print(f"Applied {100-(magenta_factor*100):.0f}% magenta reduction.")
            
        except Exception as e:
            print(f"Could not apply magenta reduction: {e}")
        # --- END FIX ---
        
        
        # Create a reportlab ImageReader object from the in-memory CMYK image
        back_image_for_pdf = ImageReader(pil_image_cmyk)
        print("Image converted successfully.")
        
    except Exception as e:
        print(f"Error: Failed to load or convert image with Pillow: {e}")
        print("Please ensure 'Pillow' is installed (pip install Pillow)")
        return
    # --- END: Image Conversion ---

    # --- Place Images on PDF Grid (Mirrored and Centered Layout) ---
    for i in range(cards_per_page):
        row = i // cards_per_row
        col = i % cards_per_row

        # --- COORDINATE CALCULATION (Centered and Mirrored) ---
        inverted_col = (cards_per_row - 1 - col)
        x = grid_origin_x + inverted_col * (card_width + spacing)
        
        inverted_row = (cards_per_col - 1 - row)
        y = grid_origin_y + (inverted_row * (card_height + spacing))
        
        # Draw the CMYK ImageReader object
        c.drawImage(back_image_for_pdf, x, y, width=card_width, height=card_height)

    # --- Finalize PDF ---
    c.save()
    
    print(f"Successfully generated centered CMYK back-side PDF: {output_pdf}")


if __name__ == "__main__":
    back_image_file = 'back.png'
    output_pdf_file = 'back_layout_CMYK.pdf'

    if not os.path.exists(back_image_file):
        print(f"Error: The file '{back_image_file}' was not found in this directory.")
        print("Please ensure you have a 'back.png' file in the same folder as the script.")
    else:
        create_back_pdf_layout(back_image_file, output_pdf_file)