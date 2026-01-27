import torch
from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor
from PIL import Image

input_file = input('input file: ') or 'input.jpg'
output_file = 'output.txt'

if torch.cuda.is_available():
    device = "cuda"
    dtype = torch.bfloat16
elif torch.backends.mps.is_available():
    device = "mps"
    dtype = torch.float32
else:
    device = "cpu"
    dtype = torch.float32
print(f"Using device: {device}   dtype: {dtype}")
print("Loading model...")
model = LightOnOcrForConditionalGeneration.from_pretrained(
    "lightonai/LightOnOCR-2-1B",
    torch_dtype=dtype,
    trust_remote_code=True).to(device)
processor = LightOnOcrProcessor.from_pretrained(
    "lightonai/LightOnOCR-2-1B",
    trust_remote_code=True)
image = Image.open(input_file).convert("RGB")
conversation = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "Read all the text in the image."}
        ]
    }
]
inputs = processor.apply_chat_template(
    conversation,
    add_generation_prompt=True,
    tokenize=False)
inputs = processor(
    text=inputs,
    images=image,
    return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}
if dtype == torch.bfloat16 and device == "cuda":
    inputs["pixel_values"] = inputs["pixel_values"].to(dtype)
print("Generating...")
output_ids = model.generate(
    **inputs,
    max_new_tokens=2048,
    do_sample=False,
    temperature=0.0,
    num_beams=1,)
generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]
text = processor.decode(generated_ids, skip_special_tokens=True)
with open(output_file, "w", encoding="utf-8") as f:
    f.write(text)
print(f"\nDone. Result saved to {output_file}")
print(text)

