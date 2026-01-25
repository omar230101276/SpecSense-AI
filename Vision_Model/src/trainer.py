from ultralytics import YOLO
import torch
import os
from pathlib import Path

# Config
DATA_YAML_PATH = '../data.yaml' # Relative to src/ if run from there? Or make absolute?
MODEL_SIZE = 'yolov8m-seg.pt' 
EPOCHS = 150
BATCH_SIZE = 8 
IMG_SIZE = 640

def train_yolov8():
    """Initializes and trains the YOLOv8 segmentation model."""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"--- Starting Training on Device: {device.upper()} ---")

    try:
        model = YOLO(MODEL_SIZE)
        results = model.train(
            data=DATA_YAML_PATH,     
            epochs=EPOCHS,           
            imgsz=IMG_SIZE,          
            batch=BATCH_SIZE,        
            device=device,           
            name='cable_analysis_v1' 
        )
        save_dir = Path(results.save_dir)
        best_model_path = save_dir / 'weights' / 'best.pt'
        print(f"\nTraining Complete. Best model saved to: {best_model_path}")
        return best_model_path

    except Exception as e:
        print(f"An error occurred during training: {e}")
        return None

if __name__ == "__main__":
    train_yolov8()
