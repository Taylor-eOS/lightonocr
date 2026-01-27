model_name = "lightonai/LightOnOCR-2-1B"
ocr_instruction = "Extract the text as flowing paragraphs. Join hyphenated words at line breaks. Preserve only actual paragraph breaks. Omit image captions."
default_input_file = 'input.jpg'
default_input_folder = 'input_images'
output_file = 'output.txt'
print_limit = 1800
separator = '\n\n---\n\n'
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp')

