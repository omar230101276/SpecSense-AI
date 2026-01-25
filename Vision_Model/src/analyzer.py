import cv2
import os
import sys
from ultralytics import YOLO

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Vision_Model.config.settings import PIXELS_PER_MM, CONF_THRESHOLD, get_cable_specs
from Vision_Model.src.utils import load_image_robust

# Auto-locate model (default to best.pt in models folder)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Points to ../models/best.pt
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "models", "best.pt")

def analyze_cable_image(image_path, model_path=None):
    """
    Analyzes a cable cross-section image using YOLOv8 AI model.
    """
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH

    # 1. Load Model
    try:
        model = YOLO(model_path)
    except Exception as e:
        return None, [{"Error": f"Model failed to load at {model_path}: {e}"}]

    # 2. Load Image
    img = load_image_robust(image_path)
    if img is None:
        return None, [{"Error": "Failed to load/decode image."}]

    # 3. Inference
    results = model(img, conf=CONF_THRESHOLD, verbose=False)
    
    all_detections = []
    if results[0].boxes:
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            width_px = x2 - x1
            area = width_px * (y2 - y1)
            diameter_mm = width_px / PIXELS_PER_MM
            
            all_detections.append({
                "box": (x1, y1, x2, y2),
                "width_px": width_px,
                "diameter_mm": diameter_mm,
                "area": area,
                "conf": float(box.conf)
            })

    # Filter: Largest only
    final_output = []
    if all_detections:
        all_detections.sort(key=lambda x: x['area'], reverse=True)
        main_cable = all_detections[0]
        
        # Get Engineering Specs
        specs = get_cable_specs(main_cable['diameter_mm'])
        
        # QC Status
        status = "PASS" if main_cable['diameter_mm'] > 5.0 else "FAIL (Too Small)"
        color = (0, 255, 0) if "PASS" in status else (0, 0, 255)
        
        # Draw Visuals
        x1, y1, x2, y2 = main_cable['box']
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        
        label_text = f"Dia: {main_cable['diameter_mm']:.1f} mm"
        (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(img, (x1, y1 - 30), (x1 + text_w + 20, y1), color, -1)
        cv2.putText(img, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Merge results
        result_dict = {
            "Diameter (mm)": round(main_cable['diameter_mm'], 2),
            "Status": status,
            **specs
        }
        final_output.append(result_dict)

    if not final_output:
        return img, [{"Error": "No cable detected."}]
        
    return img, final_output
