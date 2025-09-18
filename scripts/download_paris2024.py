#!/usr/bin/env python3
import kagglehub
import shutil
import os

# Download latest version
path = kagglehub.dataset_download("piterfm/paris-2024-olympic-summer-games")
print("Path to dataset files:", path)

# Copy files to raw directory
raw_dir = "raw"
os.makedirs(raw_dir, exist_ok=True)

# List files in downloaded directory
for file in os.listdir(path):
    if file.endswith('.csv'):
        src = os.path.join(path, file)
        dst = os.path.join(raw_dir, f"paris2024_{file}")
        shutil.copy2(src, dst)
        print(f"Copied: {file} -> {dst}")
