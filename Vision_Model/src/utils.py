import cv2
import numpy as np
import os

def load_image_robust(image_path):
    """
    Robust image loading that handles Windows paths with spaces/special chars.
    """
    try:
        # Read file as byte stream
        img_stream = np.fromfile(image_path, dtype=np.uint8)
        # Decode image
        img = cv2.imdecode(img_stream, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Image decoding failed (Result is None).")
        return img    
    except Exception as e:
        print(f"Error loading image: {e}")
        return None
