import os
from ocr_file import load_model, process_image
from settings import default_input_folder, separator, ocr_instruction, image_extensions

def get_image_files(folder_path):
    if not os.path.isdir(folder_path):
        return []
    all_files = []
    try:
        for item in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item)
            if os.path.isfile(full_path):
                all_files.append(full_path)
    except PermissionError as e:
        print(f"Permission denied accessing folder: {e}")
        return []
    except Exception as e:
        print(f"Error reading folder: {e}")
        return []
    image_files = [f for f in all_files if f.lower().endswith(image_extensions)]
    image_files.sort()
    return image_files

def process_folder():
    user_input = input('Input folder name: ').strip() or default_input_folder
    if not os.path.isdir(user_input):
        print(f"Error: Folder '{user_input}' not found.")
        return
    print(f"Using input folder: {user_input}")
    image_files = get_image_files(user_input)
    if not image_files:
        print(f"No image files found in folder '{user_input}'")
        print(f"Supported formats: {', '.join(image_extensions)}")
        return
    print(f"Found {len(image_files)} image file(s)")
    model, processor, device, dtype = load_model()
    #print(f"Using device: {device}, dtype: {dtype}")
    print(f"Processing images with instruction: {ocr_instruction}")
    batch_output_file = user_input + '.txt'
    with open(batch_output_file, 'w', encoding='utf-8') as outfile:
        for idx, image_path in enumerate(image_files, 1):
            filename = os.path.basename(image_path)
            print(f"Processing {idx}/{len(image_files)}: {filename}")
            try:
                text = process_image(model, processor, device, dtype, image_path)
                if idx > 1:
                    outfile.write(separator)
                outfile.write(f"File: {filename}\n")
                outfile.write(text)
                outfile.flush()
                print(f"Completed: {len(text)} characters")
            except FileNotFoundError:
                error_msg = f"Error: {filename} not found"
                print(f"{error_msg}")
                if idx > 1:
                    outfile.write(separator)
                outfile.write(f"File: {filename}\n{error_msg}\n")
                outfile.flush()
            except Exception as e:
                error_msg = f"Error processing {filename}: {str(e)}"
                print(f"{error_msg}")
                if idx > 1:
                    outfile.write(separator)
                outfile.write(f"File: {filename}\n{error_msg}\n")
                outfile.flush()
    print(f"All results saved to {batch_output_file}")
    print(f"Processed {len(image_files)} image{'s' if len(image_files) != 1 else ''}")

if __name__ == "__main__":
    process_folder()

