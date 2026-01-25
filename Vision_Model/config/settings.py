
# ==========================================
# ⚙️ VISION MODULE PARAMETERS
# ==========================================

# 1. CALIBRATION
# Number of pixels representing 1 millimeter.
# Calibrated based on reference object (Adjust if camera height changes).
PIXELS_PER_MM = 18.5 

# 2. AI THRESHOLDS
# Minimum score (0-1) to accept a detection.
CONF_THRESHOLD = 0.01

# 3. ENGINEERING RULES
# Rules for estimating cable specs based on diameter (mm)
def get_cable_specs(diameter_mm):
    """
    Returns technical specs based on cable diameter (Standard Estimation).
    """
    if diameter_mm >= 40:
        return {
            "Voltage Class": "Medium Voltage (11 kV - 33 kV)",
            "Conductor": "Class 2 (Compacted Copper/Al)",
            "Insulation": "XLPE + Semi-conductive Layer",
            "Sheath Mat.": "HDPE / PVC (Red/Black)",
            "Cable Type": "Heavy Duty Power Feeder"
        }
    elif 15 <= diameter_mm < 40:
        return {
            "Voltage Class": "Low Voltage (0.6/1 kV)",
            "Conductor": "Class 2 (Stranded Copper)",
            "Insulation": "XLPE (Cross-linked PE)",
            "Sheath Mat.": "PVC (Black/UV Resistant)",
            "Cable Type": "Power Cable (Armoured)"
        }
    else:
        return {
            "Voltage Class": "Low Voltage (300/500 V)",
            "Conductor": "Class 1 (Solid Copper)",
            "Insulation": "PVC (Polyvinyl Chloride)",
            "Sheath Mat.": "PVC (Grey/White)",
            "Cable Type": "Control/Light Duty"
        }
