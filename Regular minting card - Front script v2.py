import os
import re
from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
import math  # <-- NEW: Import math for ceiling function

# ==============================================================================
# PART 1: QR Code Generation and Merging
# ==============================================================================

# (This entire section remains unchanged)

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
    image_outer = Image.open(image_outer_path)
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

        original_counter_match = re.search(r'QR_(\d+)_', filename)
        original_counter = original_counter_match.group(1) if original_counter_match else "X"
        
        merged_filename = f"{base_filename}_{original_counter}_{code}.png"
        output_filepath = os.path.join(output_folder, merged_filename)

        image_combined.save(output_filepath)
        print(f"Merged image {filename} saved as {output_filepath}")
        merged_image_paths.append(output_filepath)
        
    return merged_image_paths

# ==============================================================================
# PART 2: PDF Layout and Creation
# ==============================================================================

# ==============================================================================
# PART 2: PDF Layout and Creation (MODIFIED FOR PAGE COUNT)
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

    # --- NEW: Page Counter Logic Setup ---
    total_images = len(images)
    if total_images == 0:
        print("No images to process. PDF will be empty.")
        c.save()
        return

    # This line remains unchanged, but is not used by the page_text
    total_pages = math.ceil(total_images / cards_per_page) 
    current_page = 1
    
    # Define margins for page number
    margin_right = 15 * mm 
    margin_bottom = 10 * mm
    page_num_x = page_width - margin_right
    page_num_y = margin_bottom
    # --- END: Page Counter Logic Setup ---

    for i, img_path in enumerate(images):
        if i % cards_per_page == 0 and i != 0:
            # --- MODIFIED: Draw Page Number (just number, small font) ---
            page_text = str(current_page) # <-- CHANGED
            c.setFont("Helvetica", 7)     # <-- CHANGED (from 9)
            c.drawRightString(page_num_x, page_num_y, page_text)
            # --- END: Draw Page Number ---
            
            c.showPage()
            current_page += 1 # <-- Increment page counter

        row = (i % cards_per_page) // cards_per_row
        col = (i % cards_per_page) % cards_per_row

        # --- Updated Position Calculation ---
        x = grid_origin_x + col * (card_width + spacing)
        inverted_row = (cards_per_col - 1 - row)
        y = grid_origin_y + (inverted_row * (card_height + spacing))
        # --- End Updated Calculation ---

        img = Image.open(img_path).convert("RGBA")
        target_size_px = (int(card_width_mm / 25.4 * dpi), int(card_height_mm / 25.4 * dpi))
        img = img.resize(target_size_px, Image.LANCZOS)

        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, mask=img.split()[3])

        temp_path = f"temp_{i}.jpg"
        white_bg.save(temp_path, dpi=(dpi, dpi), quality=95)
        temp_files_to_clean.append(temp_path)

        c.drawImage(temp_path, x, y, width=card_width, height=card_height)

    # --- MODIFIED: Draw Page Number on the *final* page (just number, small font) ---
    page_text = str(current_page) # <-- CHANGED
    c.setFont("Helvetica", 7)     # <-- CHANGED (from 9)
    c.drawRightString(page_num_x, page_num_y, page_text)
    # --- END: Draw Page Number ---

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
    output_pdf_path = 'cards_layout_With_Counter_RGB.pdf'
    base_filename = 'merged_image'
    font_size = 25
    counter_font_size = 20

    # --- Step 1: Generate QR Codes ---
    if not os.path.exists(qr_codes_folder):
        os.makedirs(qr_codes_folder)

    counter = 1
    with open(links_file, "r") as file:
        for url in file.readlines():
            url = url.strip()
            if url: 
                generate_qr(url, counter, qr_codes_folder)
                counter += 1
    print(f"QR codes generated successfully in the '{qr_codes_folder}' folder!")

    # --- Step 2: Merge QR codes with the base image ---
    os.makedirs(merged_images_folder, exist_ok=True)
    merged_image_paths = merge_images_inside(
        image_outer_path=base_image_path,
        qr_codes_folder=qr_codes_folder,
        output_folder=merged_images_folder,
        base_filename=base_filename,
        font_size=font_size,
        counter_font_size=counter_font_size
    )

    # --- Step 3: Create the final PDF layout ---
    create_pdf_from_images(merged_image_paths, output_pdf_path)

    # Optional: Cleanup intermediate folders if not needed
    # import shutil
    # shutil.rmtree(qr_codes_folder)
    # shutil.rmtree(merged_images_folder)
    # print("Cleaned up intermediate folders.")