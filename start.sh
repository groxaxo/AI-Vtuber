#!/bin/bash
source "$(conda info --base)/etc/profile.d/conda.sh"

# Create environment if it doesn't exist
if ! conda info --envs | grep -q "ai-vtuber"; then
    echo "Creating conda environment ai-vtuber..."
    conda create -n ai-vtuber python=3.10 -y
fi

conda activate ai-vtuber

# Install system dependencies via conda
echo "Installing ffmpeg and portaudio..."
conda install -c conda-forge ffmpeg portaudio pyaudio -y

# Install python dependencies
echo "Installing python requirements..."
pip install requests
pip install nicegui
pip install -r requirements.txt

echo "Starting AI-Vtuber..."
python webui.py
