# SpecSense AI

**SpecSense AI** is an advanced OCR and AI-powered system designed for the automated parsing of cable specifications and keyword generation. It leverages computer vision and natural language processing to extract, correct, and validate technical data from documents and images.

## Features

- **Automated Extraction**: Extracts technical specifications (Voltage, Current, Armour, etc.) from cable datasheets and images.
- **AI-Powered OCR**: Uses EasyOCR and PyTorch for robust text recognition.
- **Keyword Generation**: Generates relevant keywords for cable products to improve searchability and categorization.
- **Validation Engine**: Validates extracted data against engineering standards.
- **User Interface**: Interactive web interface built with Streamlit for easy uploading and verification.

## Project Structure

- **`OCR_Reader/`**: Core OCR engine and extraction logic (including Spacy and regex parsers).
- **`Keyword_Generator/`**: Module for generating listing keywords from cable descriptions.
- **`Vision_Model/`**: Computer vision models (YOLO) for detecting cable structures/tables.
- **`Validator/`**: Logic to validate and correct extracted specifications.
- **`app.py`**: Main entry point for the Streamlit web application.
- **`SpecSense.bat`**: Automated setup and startup script for Windows.

## Installation & Usage

### Method 1: Automated (Recommended)

Simply run the provided batch script:
```cmd
SpecSense.bat
```
This script will automatically:
1. Create a Python virtual environment (`venv`).
2. Install all required dependencies from `requirements.txt`.
3. Launch the Streamlit application in your default browser.

### Method 2: Manual Setup

1. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Key Technologies

- **Python**: Core programming language.
- **Streamlit**: Web interface.
- **PyTorch**: Deep learning framework.
- **EasyOCR**: Optical Character Recognition.
- **Ultralytics (YOLO)**: Object detection for document layout analysis.
- **Spacy**: Natural Language Processing for entity extraction.
