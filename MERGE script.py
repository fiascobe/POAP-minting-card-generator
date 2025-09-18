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

def merge_images_inside(image_outer_path, qr_codes_folder, output_folder, base_filename, font_size=100):
    """
    Merges QR code images with a base design and adds a 6-character code.
    """
    image_outer = Image.open(image_outer_path)
    font_path = "rubik.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
        print(f"Loaded font from: {font_path}")
    except Exception as e:
        print(f"Failed to load font '{font_path}': {e}")
        font = ImageFont.load_default()
        print("Falling back to default font.")

    merged_image_paths = []
    for filename in sorted(os.listdir(qr_codes_folder)):
        if filename.startswith("QR_") and filename.endswith(".png"):
            qr_filepath = os.path.join(qr_codes_folder, filename)
            image_inner = Image.open(qr_filepath).convert("RGB")

            match = re.search(r'QR_\d+_([A-Za-z0-9]{6})\.png', filename)
            code = match.group(1) if match else "######"

            paste_position = (214, 528)
            qr_x, qr_y = paste_position

            image_combined = image_outer.copy()
            image_combined.paste(image_inner, paste_position)

            draw = ImageDraw.Draw(image_combined)
            text = code

            # Calculate text size using textbbox (Pillow 10+)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            text_x = qr_x + (image_inner.width - text_width) // 2
            text_y = qr_y + image_inner.height + 45

            draw.text((text_x, text_y), text, font=font, fill="black")

            merged_filename = f"{base_filename}_{filename.replace('QR_', '').replace('.png', '')}.png"
            output_filepath = os.path.join(output_folder, merged_filename)

            image_combined.save(output_filepath)
            print(f"Merged image {filename} saved as {output_filepath}")
            merged_image_paths.append(output_filepath)
            
    return merged_image_paths

# ==============================================================================
# PART 2: PDF Layout and Creation
# ==============================================================================

def draw_crop_marks(c, cx, cy, card_width, card_height, crop_length, crop_offset):
    """Draws crop marks around a card's position on the canvas."""
    # Horizontal marks
    c.line(cx - crop_offset, cy, cx - crop_offset - crop_length, cy)
    c.line(cx + card_width + crop_offset, cy, cx + card_width + crop_offset + crop_length, cy)
    c.line(cx - crop_offset, cy + card_height, cx - crop_offset - crop_length, cy + card_height)
    c.line(cx + card_width + crop_offset, cy + card_height, cx + card_width + crop_offset + crop_length, cy + card_height)

    # Vertical marks
    c.line(cx, cy - crop_offset, cx, cy - crop_offset - crop_length)
    c.line(cx, cy + card_height + crop_offset, cx, cy + card_height + crop_offset + crop_length)
    c.line(cx + card_width, cy - crop_offset, cx + card_width, cy - crop_offset - crop_length)
    c.line(cx + card_width, cy + card_height + crop_offset, cx + card_width, cy + card_height + crop_offset + crop_length)

def create_pdf_from_images(images, output_pdf):
    """Lays out merged images onto an A4 PDF with crop marks."""
    # Configuration
    card_width_mm, card_height_mm = 57, 85
    cards_per_row, cards_per_col = 3, 3
    offset_x_mm, offset_y_mm = 10, 10
    crop_mark_length, crop_mark_offset = 3, 0.5
    dpi = 300

    # Convert to points
    card_width = card_width_mm * mm
    card_height = card_height_mm * mm
    offset_x = offset_x_mm * mm
    offset_y = offset_y_mm * mm
    crop_length = crop_mark_length * mm
    crop_offset = crop_mark_offset * mm

    c = canvas.Canvas(output_pdf, pagesize=A4)
    cards_per_page = cards_per_row * cards_per_col
    temp_files_to_clean = []

    for i, img_path in enumerate(images):
        if i % cards_per_page == 0 and i != 0:
            c.showPage()

        row = (i % cards_per_page) // cards_per_row
        col = (i % cards_per_page) % cards_per_row

        x = offset_x + col * card_width
        y = A4[1] - offset_y - (row + 1) * card_height

        img = Image.open(img_path).convert("RGBA")
        target_size_px = (int(card_width_mm / 25.4 * dpi), int(card_height_mm / 25.4 * dpi))
        img = img.resize(target_size_px, Image.LANCZOS)

        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, mask=img.split()[3])

        temp_path = f"temp_{i}.jpg"
        white_bg.save(temp_path, dpi=(dpi, dpi), quality=95)
        temp_files_to_clean.append(temp_path)

        c.drawImage(temp_path, x, y, width=card_width, height=card_height)
        draw_crop_marks(c, x, y, card_width, card_height, crop_length, crop_offset)

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
    base_image_path = 'base.png'
    qr_codes_folder = 'QR Codes'
    merged_images_folder = 'Merged Images'
    output_pdf_path = 'cards_layout.pdf'
    base_filename = 'merged_image'
    font_size = 20

    # --- Step 1: Generate QR Codes ---
    if not os.path.exists(qr_codes_folder):
        os.makedirs(qr_codes_folder)

    counter = 1
    generated_qr_paths = []
    with open(links_file, "r") as file:
        for url in file.readlines():
            url = url.strip()
            qr_path = generate_qr(url, counter, qr_codes_folder)
            generated_qr_paths.append(qr_path)
            counter += 1
    print(f"QR codes generated successfully in the '{qr_codes_folder}' folder!")

    # --- Step 2: Merge QR codes with the base image ---
    os.makedirs(merged_images_folder, exist_ok=True)
    merged_image_paths = merge_images_inside(
        base_image_path,
        qr_codes_folder,
        merged_images_folder,
        base_filename,
        font_size=font_size
    )

    # --- Step 3: Create the final PDF layout ---
    create_pdf_from_images(merged_image_paths, output_pdf_path)

    # Optional: Cleanup intermediate folders if not needed
    # import shutil
    # shutil.rmtree(qr_codes_folder)
    # shutil.rmtree(merged_images_folder)
    # print("Cleaned up intermediate folders.")
