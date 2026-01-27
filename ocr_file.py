import torch
from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor
from PIL import Image

output_file = 'output.txt'

def get_device_and_dtype():
    if torch.cuda.is_available():
        return "cuda", torch.bfloat16
    if torch.backends.mps.is_available():
        return "mps", torch.float32
    return "cpu", torch.float32

def load_model_and_processor():
    device, dtype = get_device_and_dtype()
    model = LightOnOcrForConditionalGeneration.from_pretrained("lightonai/LightOnOCR-2-1B", torch_dtype=dtype, trust_remote_code=True).to(device)
    processor = LightOnOcrProcessor.from_pretrained("lightonai/LightOnOCR-2-1B", trust_remote_code=True)
    return model, processor, device, dtype

def load_image(image_path):
    return Image.open(image_path).convert("RGB")

def prepare_inputs(processor, image):
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": "Read all the text in the image."}
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

def save_text(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    user_input = input('Full input file: ').strip() or 'input.jpg'
    candidates = [user_input, user_input + '.jpg', user_input + '.jpeg', user_input + '.png']
    input_file = None
    for candidate in candidates:
        try:
            with open(candidate, 'rb'):
                input_file = candidate
                break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error while checking file {candidate}: {e}")
            return
    if input_file is None:
        print(f"Error: File not found.")
        print(f"Tried: {', '.join(candidates)}")
        print("Please check the filename and try again.")
        return
    print(f"Using input file: {input_file}")
    print("Loading model and processor...")
    model, processor, device, dtype = load_model_and_processor()
    print(f"Using device: {device}   dtype: {dtype}")
    print("Loading image...")
    image = load_image(input_file)
    print("Preparing inputs...")
    inputs = prepare_inputs(processor, image)
    inputs = move_inputs_to_device(inputs, device, dtype)
    print("Running OCR...")
    generated_ids = generate_text(model, inputs)
    print("Decoding result...")
    text = decode_text(processor, generated_ids)
    print("Saving result...")
    save_text(text, output_file)
    print(f"Done. Result saved to {output_file}:")
    print(text.replace('\n\n', '\n'))

if __name__ == "__main__":
    main()

