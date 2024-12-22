from transformers import GPT2LMHeadModel, GPT2Config, GPT2Tokenizer
from datasets import load_dataset
from torch.utils.data import DataLoader
import torch
from torch.optim import AdamW

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

tokenizer.pad_token = tokenizer.eos_token  # Ensure padding uses eos token
tokenizer.add_special_tokens({"pad_token": tokenizer.eos_token})

# Step 1: Load the Saved Model and Tokenizer
model = GPT2LMHeadModel.from_pretrained("./gpt_proofpile2_model")
tokenizer = GPT2Tokenizer.from_pretrained("./gpt_proofpile2_model")

# Step 2: Move Model to GPU if Available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Step 3: Example of Text Generation with the Loaded Model
input_text = "The first theorem states that"
input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)

# Generate text from the model
output = model.generate(
    input_ids,
    max_length=100,    # Maximum length of generated sequence
    num_return_sequences=1,  # Number of sequences to generate
    no_repeat_ngram_size=2,  # Prevent repetition of n-grams
    top_k=50,           # Sampling from the top k logits
    top_p=0.95,         # Nucleus sampling
    temperature=0.7,    # Controls randomness
    do_sample=True      # Enable sampling
)

# Step 4: Decode and Print the Generated Text
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
