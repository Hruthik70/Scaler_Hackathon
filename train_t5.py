from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import load_dataset
import torch

# Load your dataset
dataset = load_dataset("json", data_files="dataset.json")  # We'll create this next
# Or use the dataset from dataset.py directly

tokenizer = T5Tokenizer.from_pretrained("t5-small")

def preprocess_function(examples):
    inputs = tokenizer(examples["input_text"], max_length=128, truncation=True, padding="max_length")
    labels = tokenizer(examples["target_text"], max_length=256, truncation=True, padding="max_length")
    inputs["labels"] = labels["input_ids"]
    return inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True)

# Load model
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Training args
training_args = TrainingArguments(
    output_dir="./t5-scene-model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=50,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    save_steps=100,
    eval_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    tokenizer=tokenizer,
)

trainer.train()
trainer.save_model("./t5-scene-model")
print("✅ Model saved to ./t5-scene-model")
