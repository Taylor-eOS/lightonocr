import os
from PIL import Image
import fitz
from ocr_file import load_model, process_image, save_text
import settings

def pdf_to_images(pdf_path, dpi=200):
    images = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_data = pix.tobytes("ppm")
            image = Image.frombytes("RGB", [pix.width, pix.height], img_data)
            current_max = max(image.width, image.height)
            if current_max > 1540:
                scale = 1540 / current_max
                new_width = int(image.width * scale)
                new_height = int(image.height * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            images.append(image)
        doc.close()
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

def save_image(image, page_num):
    temp_path = f"/tmp/pdf_page_{page_num}.png"
    image.save(temp_path, "PNG")
    return temp_path

def resolve_pdf_path(user_input):
    ending = '.pdf'
    if os.path.isfile(user_input):
        return user_input
    if not user_input.lower().endswith(ending):
        pdf_path = user_input + ending
        if os.path.isfile(pdf_path):
            return pdf_path
    return None

def process_pdf():
    user_input = input('PDF file name: ').strip() or settings.default_input_pdf
    file_path = resolve_pdf_path(user_input)
    if not file_path:
        print(f"Error: File '{user_input}' not found.")
        return
    print(f"Using PDF file: {file_path}")
    print(f"Converting PDF to images at {settings.pdf_dpi} DPI")
    images = pdf_to_images(file_path, settings.pdf_dpi)
    if not images:
        print("Failed to extract images from PDF")
        return
    print(f"Extracted {len(images)} page(s)")
    model, processor, device, dtype = load_model()
    pdf_base_name = os.path.splitext(file_path)[0]
    output_file = pdf_base_name + '.txt'
    print(f"Processing pages with OCR")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for page_num, image in enumerate(images, 1):
            print(f"Processing page {page_num}/{len(images)}")
            try:
                temp_path = save_image(image, page_num)
                text = process_image(model, processor, device, dtype, temp_path)
                try:
                    os.remove(temp_path)
                except:
                    pass
                if page_num > 1:
                    outfile.write(settings.separator)
                outfile.write(f"Page {page_num}\n\n")
                outfile.write(text)
                outfile.flush()
                print(f"Completed: {len(text)} characters")
            except Exception as e:
                error_msg = f"Error processing page {page_num}: {str(e)}"
                print(f"{error_msg}")
                if page_num > 1:
                    outfile.write(settings.separator)
                outfile.write(f"Page {page_num}\n{error_msg}\n\n")
                outfile.flush()
    print(f"All results saved to {output_file}")
    print(f"Processed {len(images)} page{'s' if len(images) != 1 else ''}")

if __name__ == "__main__":
    process_pdf()

