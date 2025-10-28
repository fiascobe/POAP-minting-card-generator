import os
import re
from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

# ==============================================================================
# PART 1: QR Code Generation and Merging
# ==============================================================================

def get_last_6_alphanum(url):
    """Extracts the last 6 alphanumeric characters from a URL."""
    alphanum = re.findall(r'[A-Za-z0-9]+', url)
    return ''.join(alphanum)[-6:]

def generate_qr(url, counter, output_dir):
    """
    Generates a QR code image for a given URL and saves it.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Resize the QR
    img = img.resize((294, 294), Image.LANCZOS)

    # Generate unique filename with counter and last 6 alphanum chars
    suffix = get_last_6_alphanum(url)
    filename = os.path.join(output_dir, f"QR_{counter}_{suffix}.png")
    img.save(filename)
    return filename

def merge_images_inside(image_outer_path, qr_codes_folder, output_folder, base_filename, font_size=100, counter_font_size=40):
    """
    Merges QR code images with a base design, adds a 6-character code, and a sequential counter.
    """
    # MODIFICATION 1: Load outer image as RGBA to handle transparency
    image_outer = Image.open(image_outer_path).convert("RGBA") 
    
    font_path = "rubik.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
        counter_font = ImageFont.truetype(font_path, counter_font_size)
        print(f"Loaded font from: {font_path}")
    except Exception as e:
        print(f"Failed to load font '{font_path}': {e}")
        font = ImageFont.load_default()
        counter_font = ImageFont.load_default()
        print("Falling back to default font.")

    merged_image_paths = []

    # --- START: SORTING FIX ---
    qr_files = [f for f in os.listdir(qr_codes_folder) if f.startswith("QR_") and f.endswith(".png")]

    def get_file_number(filename):
        match = re.search(r'QR_(\d+)_', filename)
        if match:
            return int(match.group(1))
        return 0 

    sorted_qr_files = sorted(qr_files, key=get_file_number)
    # --- END: SORTING FIX ---

    for i, filename in enumerate(sorted_qr_files, start=1):
        qr_filepath = os.path.join(qr_codes_folder, filename)
        image_inner = Image.open(qr_filepath).convert("RGB")

        match = re.search(r'QR_\d+_([A-Za-z0-9]{6})\.png', filename)
        code = match.group(1) if match else "######"

        paste_position = (214, 528)
        qr_x, qr_y = paste_position

        # image_combined is now RGBA since image_outer is RGBA
        image_combined = image_outer.copy() 
        image_combined.paste(image_inner, paste_position)

        draw = ImageDraw.Draw(image_combined)

        # --- Draw 6-character code ---
        text = code
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = qr_x + (image_inner.width - text_width) // 2
        text_y = qr_y + image_inner.height + 50
        draw.text((text_x, text_y), text, font=font, fill="black")

        # --- Add Counter ---
        counter_text = str(i)
        counter_color = "#000000"
        dpi = 300
        y_offset_mm = 5
        
        y_offset_px = y_offset_mm * (dpi / 25.4)
        
        img_width, img_height = image_combined.size

        counter_bbox = draw.textbbox((0, 0), counter_text, font=counter_font)
        counter_text_width = counter_bbox[2] - counter_bbox[0]
        counter_text_height = counter_bbox[3] - counter_bbox[1]

        counter_x = (img_width - counter_text_width) / 2
        counter_y = img_height - y_offset_px - counter_text_height

        draw.text((counter_x, counter_y), counter_text, font=counter_font, fill=counter_color)

        
        # MODIFICATION 2: Flatten RGBA image, convert to CMYK, and save as JPEG
        
        # --- Flatten RGBA image against a white background ---
        # Create a white RGB background
        final_rgb_image = Image.new("RGB", image_combined.size, (255, 255, 255))
        
        # Paste the combined image (with potential transparency) onto the white bg
        # This uses the alpha channel (image_combined.split()[3]) as the mask
        if image_combined.mode == 'RGBA':
            final_rgb_image.paste(image_combined, mask=image_combined.split()[3])
        else:
            final_rgb_image.paste(image_combined) # Fallback if it's not RGBA for some reason

        # --- Convert final flattened image to CMYK ---
        final_cmyk_image = final_rgb_image.convert("CMYK")
# --- START FIX: Manually reduce Magenta ---
        # This is a 'brute-force' adjustment.
        # 0.95 = 5% reduction
        # 0.90 = 10% reduction
        # Start with a small value and adjust as needed.
        magenta_factor = 0.95 

        try:
            # Split the image into its 4 CMYK channels
            c, m, y, k = final_cmyk_image.split()

            # Apply the reduction to the Magenta channel
            # .point() applies a function to every pixel in that channel
            m = m.point(lambda i: int(i * magenta_factor))

            # Re-merge the channels back into a single CMYK image
            final_cmyk_image = Image.merge("CMYK", (c, m, y, k))
            print(f"Applied {100-magenta_factor*100}% magenta reduction.")
            
        except Exception as e:
            print(f"Could not apply magenta reduction: {e}")
        # --- END FIX ---

        # --- Save as JPEG (better for CMYK) ---
        original_counter_match = re.search(r'QR_(\d+)_', filename)
        original_counter = original_counter_match.group(1) if original_counter_match else "X"
        
        # Change extension to .jpg
        merged_filename = f"{base_filename}_{original_counter}_{code}.jpg" 
        output_filepath = os.path.join(output_folder, merged_filename)

        # Save the CMYK JPEG, preserving DPI
        final_cmyk_image.save(output_filepath, quality=95, dpi=(dpi, dpi)) 
        print(f"Merged CMYK image {filename} saved as {output_filepath}")
        merged_image_paths.append(output_filepath)
        
    return merged_image_paths

# ==============================================================================
# PART 2: PDF Layout and Creation
# ==============================================================================

def create_pdf_from_images(images, output_pdf):
    """Lays out merged images onto an A4 PDF, centered on the page."""
    # Configuration
    card_width_mm, card_height_mm = 57, 85
    cards_per_row, cards_per_col = 3, 3
    spacing_mm = 5  # Spacing between cards
    dpi = 300

    # Convert to points
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

    c = canvas.Canvas(output_pdf, pagesize=A4)
    cards_per_page = cards_per_row * cards_per_col
    temp_files_to_clean = []

    for i, img_path in enumerate(images):
        if i % cards_per_page == 0 and i != 0:
            c.showPage()

        row = (i % cards_per_page) // cards_per_row
        col = (i % cards_per_page) % cards_per_col

        # --- Updated Position Calculation ---
        x = grid_origin_x + col * (card_width + spacing)
        inverted_row = (cards_per_col - 1 - row)
        y = grid_origin_y + (inverted_row * (card_height + spacing))
        # --- End Updated Calculation ---

        
        # MODIFICATION 3: Use the CMYK JPEG directly without conversion
        
        # Open the CMYK JPEG (it no longer needs .convert())
        img = Image.open(img_path) 
        
        # Resize the image
        target_size_px = (int(card_width_mm / 25.4 * dpi), int(card_height_mm / 25.4 * dpi))
        img = img.resize(target_size_px, Image.LANCZOS)

        # Save as a temporary JPEG (which is still CMYK) to be placed in the PDF
        temp_path = f"temp_{i}.jpg"
        img.save(temp_path, dpi=(dpi, dpi), quality=95)
        temp_files_to_clean.append(temp_path)
        
        # Draw the temp image
        c.drawImage(temp_path, x, y, width=card_width, height=card_height)

    c.save()
    for temp_file in temp_files_to_clean:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print(f"PDF generated: {output_pdf}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    # --- Configuration ---
    links_file = "links.txt"
    base_image_path = 'front.png'
    qr_codes_folder = 'QR Codes'
    merged_images_folder = 'Merged Images'
    output_pdf_path = 'cards_layout_with_counter_CMYK.pdf'
    base_filename = 'merged_image'
    font_size = 25
    counter_font_size = 20 # Font size for the new counter

    # --- Step 1: Generate QR Codes ---
    if not os.path.exists(qr_codes_folder):
        os.makedirs(qr_codes_folder)

    counter = 1
    # Ensure links.txt exists or handle the error
    if not os.path.exists(links_file):
        print(f"Error: '{links_file}' not found. Please create it and add URLs.")
    else:
        with open(links_file, "r") as file:
            for url in file.readlines():
                url = url.strip()
                if url: # Ensure the line is not empty
                    generate_qr(url, counter, qr_codes_folder)
                    counter += 1
        print(f"QR codes generated successfully in the '{qr_codes_folder}' folder!")

        # --- Step 2: Merge QR codes with the base image ---
        os.makedirs(merged_images_folder, exist_ok=True)
        
        if not os.path.exists(base_image_path):
             print(f"Error: '{base_image_path}' not found. This file is required.")
        else:
            merged_image_paths = merge_images_inside(
                image_outer_path=base_image_path,
                qr_codes_folder=qr_codes_folder,
                output_folder=merged_images_folder,
                base_filename=base_filename,
                font_size=font_size,
                counter_font_size=counter_font_size
            )

            # --- Step 3: Create the final PDF layout ---
            if merged_image_paths: # Only create PDF if images were merged
                create_pdf_from_images(merged_image_paths, output_pdf_path)
            else:
                print("No images were merged, PDF creation skipped.")

    # Optional: Cleanup intermediate folders if not needed
    # import shutil
    # shutil.rmtree(qr_codes_folder)
    # shutil.rmtree(merged_images_folder)
    # print("Cleaned up intermediate folders.")