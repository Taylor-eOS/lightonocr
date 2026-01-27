import re
import torch
from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor
from PIL import Image
from settings import default_input_file, print_limit, ocr_instruction, image_extensions, model_name

def get_device():
    if torch.cuda.is_available():
        return "cuda", torch.bfloat16
    if torch.backends.mps.is_available():
        return "mps", torch.float32
    return "cpu", torch.float32

def load_model():
    print("Loading model")
    device, dtype = get_device()
    model = LightOnOcrForConditionalGeneration.from_pretrained(model_name, torch_dtype=dtype, trust_remote_code=True).to(device)
    processor = LightOnOcrProcessor.from_pretrained(model_name, trust_remote_code=True)
    return model, processor, device, dtype

def load_image(image_path):
    return Image.open(image_path).convert("RGB")

def prepare_inputs(processor, image, instruction):
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": instruction}
            ]
        }
    ]
    chat_text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
    inputs = processor(
        text=chat_text,
        images=image,
        return_tensors="pt")
    return inputs

def move_inputs_to_device(inputs, device, dtype):
    inputs = {k: v.to(device) for k, v in inputs.items()}
    if dtype == torch.bfloat16 and device == "cuda":
        inputs["pixel_values"] = inputs["pixel_values"].to(dtype)
    return inputs

def generate_text(model, inputs):
    output_ids = model.generate(**inputs, max_new_tokens=2048, do_sample=False, num_beams=1)
    prompt_length = inputs["input_ids"].shape[1]
    generated_ids = output_ids[0, prompt_length:]
    return generated_ids

def decode_text(processor, generated_ids):
    return processor.decode(generated_ids, skip_special_tokens=True)

def process_image(model, processor, device, dtype, image_path, instruction=None):
    if instruction is None:
        instruction = ocr_instruction
    image = load_image(image_path)
    inputs = prepare_inputs(processor, image, instruction)
    inputs = move_inputs_to_device(inputs, device, dtype)
    generated_ids = generate_text(model, inputs)
    text = decode_text(processor, generated_ids)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    return text

def save_text(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def find_file(base_name, extensions=None):
    if extensions is None:
        extensions = image_extensions
    candidates = [base_name]
    for ext in extensions:
        candidates.append(base_name + ext)
    for candidate in candidates:
        try:
            with open(candidate, 'rb'):
                return candidate
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error while checking file {candidate}: {e}")
            return None
    print(f"Error: File not found.")
    print(f"Tried: {', '.join(candidates)}")
    print("Please check the filename and try again.")
    return None

def read_file():
    user_input = input('Full input file name: ').strip() or default_input_file
    input_file = find_file(user_input)
    if input_file is None:
        return
    print(f"Using input file: {input_file}")
    model, processor, device, dtype = load_model()
    #print(f"Using device: {device}, dtype: {dtype}")
    print("Running OCR")
    print(ocr_instruction)
    text = process_image(model, processor, device, dtype, input_file)
    print("Saving result")
    output_file = os.path.basename(input_file)
    save_text(text, output_file)
    print(f"Result saved to {output_file}:")
    ellipsis = ''
    if len(text) > print_limit:
        ellipsis = '...[truncated]'
    print(text[:print_limit] + ellipsis)

if __name__ == "__main__":
    read_file()

