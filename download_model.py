from huggingface_hub import snapshot_download
import os

# Define the model to download and the local directory to save it to
model_id = "google/gemma-2b-it"
local_dir = "local_gemma_model"

# Create the directory if it doesn't exist
os.makedirs(local_dir, exist_ok=True)

print(f"Downloading model '{model_id}' to '{local_dir}'...")
print("This may take a few minutes...")

# Download the model snapshot
snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False # Set to False for Windows compatibility
)

print(f"✅ Model downloaded successfully to '{local_dir}'!")