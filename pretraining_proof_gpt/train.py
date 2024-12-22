from transformers import GPT2LMHeadModel, GPT2Config, GPT2Tokenizer
from datasets import load_dataset
from torch.utils.data import DataLoader
import torch
from torch.optim import AdamW

# Step 1: Load Proof-Pile-2 Dataset
dataset = load_dataset("EleutherAI/proof-pile-2", 'default', split="train[:1%]")

# Step 2: Load Tokenizer and Define Configuration for GPT Model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Adjust tokenizer to handle the special tokens in the dataset (if necessary)
tokenizer.pad_token = tokenizer.eos_token  # Ensure padding uses eos token
tokenizer.add_special_tokens({"pad_token": tokenizer.eos_token})

config = GPT2Config(
    vocab_size=tokenizer.vocab_size,  # Ensure vocab size matches tokenizer
    n_positions=1024,                  # Sequence length
    n_ctx=1024,                        # Context size
    n_embd=768,                        # Embedding size
    n_layer=12,                        # Number of layers
    n_head=12,                         # Number of attention heads
    layer_norm_epsilon=1e-5,
    activation_function="gelu",
)

# Step 3: Initialize Model with Random Weights
model = GPT2LMHeadModel(config)

# Step 4: Tokenize the Dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=1024)

# Apply the tokenizer to the dataset
tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# Step 5: Create DataLoader for Training
# Prepare the dataset for training
train_dataset = tokenized_datasets["train"]
train_dataloader = DataLoader(train_dataset, batch_size=4, shuffle=True)

# Step 6: Set Up Optimizer
optimizer = AdamW(model.parameters(), lr=5e-5)

# Step 7: Training Loop
model.train()  # Set the model to training mode
for epoch in range(1):  # Set the number of epochs you want
    for batch in train_dataloader:
        input_ids = batch["input_ids"].to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        labels = input_ids  # In language modeling, labels are the same as input IDs
        
        optimizer.zero_grad()
        outputs = model(input_ids, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()

        print(f"Loss: {loss.item()}")

# Step 8: Save the Model (optional)
model.save_pretrained("./gpt_proofpile2_model")
tokenizer.save_pretrained("./gpt_proofpile2_model")
