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
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if mins > 0 or hours > 0:
        time_parts.append(f"{mins} minute{'s' if mins > 1 else ''}")
    if secs > 0 or len(time_parts) == 0:
        time_parts.append(f"{secs} second{'s' if secs > 1 else ''}")
    return ' '.join(time_parts)

def process_pdf():
    user_input = input('PDF file name: ').strip() or settings.default_input_pdf
    file_path = resolve_pdf_path(user_input)
    if not file_path:
        print(f"Error: File '{user_input}' not found.")
        return
    print(f"Using PDF file: {file_path}")
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return
    total_pages = len(doc)
    if total_pages == 0:
        print("The PDF has no pages.")
        doc.close()
        return
    print(f"The PDF has {total_pages} page{'s' if total_pages > 1 else ''}.")
    start_input = input(f"Enter starting page number (1-{total_pages}, press Enter for 1): ").strip()
    if not start_input:
        start_page = 1
    else:
        try:
            proposed = int(start_input)
            if 1 <= proposed <= total_pages:
                start_page = proposed
            else:
                print("Page number out of range, starting from page 1.")
                start_page = 1
        except ValueError:
            print("Invalid input, starting from page 1.")
            start_page = 1
    print(f"Processing pages {start_page} to {total_pages}")
    num_to_process = total_pages - start_page + 1
    model, processor, device, dtype = load_model()
    pdf_base_name = os.path.splitext(file_path)[0]
    output_file = pdf_base_name + '.txt'
    print(f"Processing pages with OCR at {settings.pdf_dpi} DPI")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        total_start_time = time.time()
        running_time_sum = 0.0
        for proc_idx in range(num_to_process):
            page_num = start_page + proc_idx
            print(f"Processing page {page_num}/{total_pages} (progress {proc_idx + 1}/{num_to_process})")
            page_start_time = time.time()
            try:
                page = doc.load_page(page_num - 1)
                image = get_page_image(page, settings.pdf_dpi)
                temp_path = save_image(image, page_num)
                text = process_image(model, processor, device, dtype, temp_path)
                try:
                    os.remove(temp_path)
                except:
                    pass
                if proc_idx > 0:
                    outfile.write(settings.separator)
                outfile.write(f"Page {page_num}\n\n")
                outfile.write(text)
                outfile.flush()
                print(f"Completed: {len(text)} characters")
            except Exception as e:
                error_msg = f"Error processing page {page_num}: {str(e)}"
                print(error_msg)
                if proc_idx > 0:
                    outfile.write(settings.separator)
                outfile.write(f"Page {page_num}\n{error_msg}\n\n")
                outfile.flush()
            page_duration = time.time() - page_start_time
            running_time_sum += page_duration
            pages_processed = proc_idx + 1
            avg_time = running_time_sum / pages_processed
            print(f"Page {page_num} took {page_duration:.2f} seconds (average {avg_time:.2f} s/page)")
            remaining_pages = num_to_process - pages_processed
            if remaining_pages > 0:
                est_remaining_seconds = avg_time * remaining_pages
                print(f"Estimated time left for remaining {remaining_pages} page{'s' if remaining_pages > 1 else ''}: {format_duration(est_remaining_seconds)}")
        total_duration = time.time() - total_start_time
        print(f"Total OCR processing time: {format_duration(total_duration)}")
    doc.close()
    print(f"All results saved to {output_file}")
    print(f"Processed {num_to_process} page{'s' if num_to_process != 1 else ''} from {start_page} to {total_pages}")

if __name__ == "__main__":
    process_pdf()

