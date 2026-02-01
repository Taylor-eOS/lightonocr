import os
import time
import fitz
from PIL import Image
from ocr_file import load_model, process_image, save_text
import settings

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

def get_page_image(page, dpi):
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_data = pix.tobytes("ppm")
    image = Image.frombytes("RGB", [pix.width, pix.height], img_data)
    current_max = max(image.width, image.height)
    if current_max > 1540:
        scale = 1540 / current_max
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image

def format_duration(seconds):
    seconds = max(seconds, 0.0)
    total_minutes = seconds / 60.0
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    if total_minutes < 1:
        return "1 minute"
    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0 or hours == 0:
        time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    return ' '.join(time_parts)

def ask_for_pdf_path():
    user_input = input('PDF file name: ').strip() or settings.default_input_pdf
    file_path = resolve_pdf_path(user_input)
    if not file_path:
        print(f"Error: File '{user_input}' not found.")
        return None
    print(f"Using PDF file: {file_path}")
    return file_path

def open_pdf_document(file_path):
    try:
        doc = fitz.open(file_path)
        if len(doc) == 0:
            print("No pages detected in file.")
            doc.close()
            return None
        print(f"The PDF has {len(doc)} page{'s' if len(doc) > 1 else ''}.")
        return doc
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return None

def ask_for_start_page(total_pages):
    while True:
        start_input = input(f"Enter starting page number (1-{total_pages}), default to 1: ").strip()
        if not start_input:
            return 1
        try:
            proposed = int(start_input)
            if 1 <= proposed <= total_pages:
                return proposed
            print(f"Page number must be between 1 and {total_pages}. Try again.")
        except ValueError:
            print("Number out of range. Please enter a valid number.")

def process_single_page(page_num, page, model, processor, device, dtype, outfile, is_first, separator):
    print(f"Processing page {page_num}")
    page_start = time.time()
    try:
        image = get_page_image(page, settings.pdf_dpi)
        temp_path = save_image(image, page_num)
        text = process_image(model, processor, device, dtype, temp_path)
        try:
            os.remove(temp_path)
        except:
            pass
        if not is_first:
            outfile.write(separator)
        outfile.write(f"Page {page_num}\n\n")
        outfile.write(text)
        outfile.flush()
        print(f"Completed {len(text)} characters")
    except Exception as e:
        error_msg = f"Error processing page {page_num}: {str(e)}"
        print(error_msg)
        if not is_first:
            outfile.write(separator)
        outfile.write(f"Page {page_num}\n{error_msg}\n\n")
        outfile.flush()
    duration = time.time() - page_start
    return duration

def run_ocr_loop(doc, start_page, model, processor, device, dtype, output_file):
    total_pages = len(doc)
    num_to_process = total_pages - start_page + 1
    print(f"Processing pages {start_page} to {total_pages} at {settings.pdf_dpi} DPI")
    total_start = time.time()
    running_sum = 0.0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for idx in range(num_to_process):
            page_num = start_page + idx
            print(f"Progress {idx + 1}/{num_to_process}")
            duration = process_single_page(page_num, doc.load_page(page_num - 1), model, processor, device, dtype, outfile, idx == 0, settings.separator)
            running_sum += duration
            processed = idx + 1
            avg = running_sum / processed
            print(f"Page {page_num} took {duration:.0f} seconds (average {avg:.0f} per page)")
            remaining = num_to_process - processed
            if remaining > 0:
                est_sec = avg * remaining
                print(f"Estimated time for remaining {remaining} pages: {format_duration(est_sec)}")
        total_dur = time.time() - total_start
        print(f"Total OCR processing time: {format_duration(total_dur)}")
    return num_to_process, total_pages

def process_pdf():
    file_path = ask_for_pdf_path()
    if not file_path:
        return
    doc = open_pdf_document(file_path)
    if not doc:
        return
    start_page = ask_for_start_page(len(doc))
    model, processor, device, dtype = load_model()
    pdf_base_name = os.path.splitext(file_path)[0]
    output_file = pdf_base_name + '.txt'
    processed_count, total_pages = run_ocr_loop(doc, start_page, model, processor, device, dtype, output_file)
    doc.close()
    print(f"All results saved to {output_file}")
    print(f"Processed {processed_count} page{'s' if processed_count != 1 else ''} from {start_page} to {total_pages}")

if __name__ == "__main__":
    process_pdf()

