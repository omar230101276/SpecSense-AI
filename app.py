import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import tempfile

# Module Imports
# Ensure these match your folder structure
from Vision_Model import analyze_cable_image
from OCR_Reader.src.core_ocr import OCREngine
from OCR_Reader.src.extraction import SpecificationExtractor, SpecCorrector
from OCR_Reader.src.validation import CableValidator
from Keyword_Generator.keyword_tool import KeywordExtractor, CableClassifier
from Assistant_Module.assistant_engine import run_assistant_pipeline
from Assistant_Module.llm_service import explain_cable_selection, explain_internal_wiring
from Assistant_Module.internal_wiring_engine import InternalWiringEngine

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SpecSense AI",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        color: #FFFFFF;
        text-align: center;
        letter-spacing: 2px;
        margin-top: -20px;
        margin-bottom: 0px;
        text-shadow: 0 0 10px rgba(77, 168, 218, 0.5);
    }
    .sub-title {
        font-size: 1.4rem;
        color: #B0B0B0;
        text-align: center;
        font-weight: 300;
        margin-bottom: 40px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4DA8DA; /* Lighter blue for dark mode */
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #C0C0C0;
        margin-bottom: 20px;
    }
    .card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .stApp {
        background-color: #0E1117;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("logo.png", width=120) 
    st.title("SpecSense AI")
    st.markdown("---")
    
    mode = st.radio(
        "Select Module:",
        ["Vision Inspection", "Datasheet/OCR Analysis", "Intelligent Technical Assistant"]
    )
    
    st.markdown("---")
    st.info("""
    **System Status:**
    ✅ Vision Module: Active
    ✅ OCR Module: Active
    ✅ Assistant Module: Active
    """)
    st.caption("v1.0.0 | Graduation Project")

# --- HEADER PRESENTATION (Global) ---
# --- HEADER PRESENTATION (Global) ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    # Use columns to center the image effectively
    sub_c1, sub_c2, sub_c3 = st.columns([1, 2, 1])
    with sub_c2:
        st.image("logo.png", use_container_width=True)
    
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.markdown('<p class="main-title">SpecSense AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Intelligent Cable Inspection & Document Analysis System</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN FUNCTIONS ---

def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# --- MODULE: VISION INSPECTION ---
if mode == "Vision Inspection":
    st.markdown('<p class="main-header">👁️ Vision Inspection Module</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Automated cable cross-section analysis and defect detection.</p>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload Cable Cross-Section (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Start AI Analysis", type="primary"):
            
            # Create tabs for each image if multiple are uploaded
            tabs = st.tabs([f"Image {i+1}" for i in range(len(uploaded_files))])
            
            for i, uploaded_file in enumerate(uploaded_files):
                with tabs[i]:
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Original Image")
                        image = Image.open(uploaded_file)
                        st.image(image, use_container_width=True)
                        
                    with st.spinner(f"Running YOLOv8 Inspection Model on {uploaded_file.name}..."):
                        # Save temp file for CV2 to read path
                        temp_path = save_uploaded_file(uploaded_file)
                        
                        if temp_path:
                            processed_img, data = analyze_cable_image(temp_path)
                            
                            # Clean up
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            
                            if processed_img is not None:
                                # Convert BGR (CV2) to RGB (Streamlit)
                                processed_img_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
                                
                                with col2:
                                    st.subheader("Analysis Results")
                                    st.image(processed_img_rgb, use_container_width=True)
                                
                                # --- METRICS DASHBOARD ---
                                st.markdown("---")
                                st.subheader("📋 Inspection Report")
                                
                                if data and isinstance(data, list):
                                    # Usually only one cable per image is the main target, but handle list
                                    for j, cable_data in enumerate(data):
                                        if "Error" in cable_data:
                                            st.error(cable_data["Error"])
                                            continue
                                        
                                        # Display Metrics
                                        m1, m2, m3, m4 = st.columns(4)
                                        m1.metric("Diameter", f"{cable_data.get('Diameter (mm)', 0)} mm")
                                        status = cable_data.get('Status', 'Unknown')
                                        m2.metric("QC Status", status, delta="PASS" if "PASS" in status else "-FAIL")
                                        m3.metric("Est. Voltage", cable_data.get('Voltage Class', 'N/A').split('(')[0].strip())
                                        m4.metric("Cable Type", cable_data.get('Cable Type', 'N/A'))
                                        
                                        # Detailed Table
                                        with st.expander(f"Full Technical Details (Cable #{j+1})", expanded=True):
                                            # FIX: Convert to string to avoid Arrow type errors
                                            st.table({k: str(v) for k, v in cable_data.items()})
                                else:
                                    st.warning("No cables detected in the image.")
                                    
                            else:
                                # Error returned in data list
                                st.error(data[0].get("Error", "Unknown Analysis Error"))

# --- MODULE: DATASHEET OCR ---
elif mode == "Datasheet/OCR Analysis":
    st.markdown('<p class="main-header">📄 Datasheet OCR & Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Extract specifications, validate engineering rules, and generate keywords.</p>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload Datasheet (PDF/Image)", type=["pdf", "png", "jpg", "jpeg", "docx"], accept_multiple_files=True)
    
    if uploaded_files and st.button("Extract & Validate All", type="primary"):
        
        tabs = st.tabs([f"Doc {i+1}: {f.name}" for i, f in enumerate(uploaded_files)])
        
        for i, uploaded_file in enumerate(uploaded_files):
            with tabs[i]:
                temp_path = save_uploaded_file(uploaded_file)
                status_container = st.container()
                
                try:
                    # 1. OCR READING
                    with status_container.status(f"Processing {uploaded_file.name}...", expanded=True) as s:
                        s.write("Initializing OCR Engine...")
                        ocr_engine = OCREngine(languages=['en']) # GPU auto-detected
                        
                        s.write("Reading Text...")
                        results = ocr_engine.read_image(temp_path, detail=0) # detail=0 for text list
                        
                        # Combine all text lines
                        full_text = " ".join(results)
                        s.write("Text Extraction Complete!")
                        
                        # 2. EXTRACTION
                        s.write("Extracting Specifications...")
                        extractor = SpecificationExtractor()
                        raw_specs = extractor.extract_specs(full_text)
                        
                        # 3. CORRECTION
                        s.write("Applying Engineering Corrections...")
                        corrector = SpecCorrector()
                        clean_specs, correction_log = corrector.correct_all(raw_specs)
                        
                        # 4. VALIDATION
                        s.write("Validating against IEC Standards...")
                        validator = CableValidator()
                        validation_result = validator.validate_cable(clean_specs)
                        
                        # 5. KEYWORDS
                        s.write("Generating Keywords & Classification...")
                        key_extractor = KeywordExtractor()
                        classifier = CableClassifier()
                        
                        keywords = key_extractor.extract_keywords(full_text)
                        category = classifier.classify(full_text)
                        
                        s.update(label="Analysis Complete!", state="complete", expanded=False)
                    
                    # --- DISPLAY RESULTS ---
                    
                    # Row 1: Extracted Data & Validation
                    c1, c2 = st.columns([3, 2])
                    
                    with c1:
                        st.subheader("📝 Extracted Specifications")
                        st.json(clean_specs)
                        
                        if correction_log:
                            with st.expander("🛠️ Correction Log (Auto-Fixes applied)"):
                                for log in correction_log:
                                    st.caption(f"- {log}")

                    with c2:
                        st.subheader("🛡️ Engineering Validation")
                        status_color = "green" if validation_result['valid'] else "red" if validation_result['status'] == 'NOT READY' else "orange"
                        st.markdown(f":{status_color}[**Status: {validation_result['status']}**]")
                        
                        if validation_result['errors']:
                            st.error("Violations Found:")
                            for err in validation_result['errors']:
                                st.markdown(f"- ❌ {err}")
                        
                        if validation_result['missing']:
                            st.warning("Missing / Unverifiable Data:")
                            for miss in validation_result['missing']:
                                st.markdown(f"- ⚠️ {miss}")
                                
                        if validation_result['valid']:
                            st.balloons()
                            st.success("✅ This cable specification meets all defined engineering standards.")

                    if validation_result['status'] != 'NOT READY':
                        st.markdown("---")
                        
                        # Row 2: Keywords & Classification
                        st.subheader("🏷️ Keyword Generation")
                        
                        k1, k2 = st.columns([1, 2])
                        with k1:
                            st.info(f"**Category Identified:**\n\n### {category}")
                        
                        with k2:
                            st.write("**Identified Keywords:**")
                            # Flatten the keyword dict for display tags
                            all_tags = []
                            for k, v in keywords.items():
                                if isinstance(v, list): all_tags.extend(v)
                                else: all_tags.append(str(v))
                            
                            st.write(", ".join([f"`{tag}`" for tag in all_tags[:20]])) # Limit display
                            
                            with st.expander("View Full Keyword JSON"):
                                st.json(keywords)

                except Exception as e:
                    st.error(f"System Error in {uploaded_file.name}: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    
                finally:
                    if temp_path and os.path.exists(temp_path):
                        os.remove(temp_path)

# --- MODULE: INTELLIGENT TECHNICAL ASSISTANT ---
# --- MODULE: INTELLIGENT TECHNICAL ASSISTANT ---
elif mode == "Intelligent Technical Assistant":
    st.markdown('<p class="main-header">💡 Intelligent Technical Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Calculate electrical loads, select cables, and get AI-powered insights.</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["External Feeder Cable", "Internal Wiring Planning"])

    with tab1:
        # CSS to style the input container similar to the screenshot
        st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"] > div:has(> div > div > div > div > h3#input-requirements) {
                background-color: #1E1E1E;
                border-left: 4px solid #FF4B4B;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<h3 id="input-requirements" style="color: white; margin-top: 0;">Input Requirements</h3>', unsafe_allow_html=True)
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border-color: #444;'/>", unsafe_allow_html=True)
            
            total_power = st.number_input("Total Estimated Power (Watts)", min_value=0.0, value=5000.0, step=100.0)
            st.markdown('<p style="color: #808495; font-size: 0.8rem; margin-top: -10px; margin-bottom: 15px;">Sum of all appliance wattages</p>', unsafe_allow_html=True)
            
            system_type = st.selectbox("System Type", ["Single Phase (e.g. 220V)", "Three Phase (e.g. 380V)"])
            sys_type_val = "three" if "Three" in system_type else "single"
            
            default_voltage = 380 if sys_type_val == "three" else 220
            voltage = st.number_input("Supply Voltage (V)", min_value=1, value=default_voltage)
            
            distance = st.number_input("Cable Distance (meters)", min_value=1.0, value=20.0, step=1.0)
            st.markdown('<p style="color: #808495; font-size: 0.8rem; margin-top: -10px; margin-bottom: 15px;">Total length from source to load</p>', unsafe_allow_html=True)
            
            # Max voltage drop is usually fixed at 5% for standard calculations, or we can keep it hidden
            max_voltage_drop_pct = 5.0

        if st.button("Calculate & Get AI Insight", type="primary"):
            appliances = [{'name': 'General Load', 'power': total_power, 'quantity': 1}]
            
            with st.spinner("Calculating..."):
                results = run_assistant_pipeline(appliances, voltage, distance, system_type=sys_type_val, max_voltage_drop_pct=max_voltage_drop_pct)
            
            with st.spinner("Generating AI Explanation..."):
                explanation = explain_cable_selection(results)
            
            st.markdown("---")
            st.subheader("📊 Calculation Results")
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Total Load", f"{results['total_power_w']} W")
            r2.metric("Current", f"{results['current_a']:.2f} A")
            r3.metric("Safe Current (w/ Margin)", f"{results['safe_current_a']:.2f} A")
            
            initial_cable_rec = results.get('initial_cable', {}).get('recommended_mm2', -1)
            cable_rec = results['cable'].get('recommended_mm2')
            r4.metric("Recommended Cable", f"{cable_rec} mm²" if cable_rec != -1 else "N/A")
            
            if results['validation_warnings']:
                for w in results['validation_warnings']:
                    st.warning(w)
                    
            if cable_rec == -1:
                st.error(results['cable'].get('error', 'Error in cable selection.'))
            else:
                if initial_cable_rec != -1 and initial_cable_rec != cable_rec:
                    st.warning(f"⚠️ **Voltage Drop Compensation:** Initial cable size ({initial_cable_rec} mm²) was insufficient due to voltage drop over {distance}m. Adjusted from **{initial_cable_rec} mm² → {cable_rec} mm²**.")
                    
                vd_status = results['voltage_drop_status']
                if "WARNING" in vd_status:
                    st.error(f"Voltage Drop: {results['voltage_drop_v']:.2f} V ({results.get('voltage_drop_pct', 0):.2f}%) - {vd_status}")
                else:
                    st.success(f"Voltage Drop: {results['voltage_drop_v']:.2f} V ({results.get('voltage_drop_pct', 0):.2f}%) - Status: {vd_status}")

            st.markdown("---")
            st.subheader("🤖 AI Engineering Assistant Insight")
            st.info(explanation)

    with tab2:
        st.markdown('### 🏢 Internal Wiring Input Parameters')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Apartment Details**")
            num_rooms = st.number_input("Number of Rooms", min_value=1, value=3, step=1)
            num_acs = st.number_input("Number of AC Units", min_value=0, value=2, step=1)
            num_lights = st.number_input("Number of Lighting Points", min_value=1, value=10, step=1)
            num_sockets = st.number_input("Number of Socket Outlets", min_value=1, value=12, step=1)
            has_kitchen = st.checkbox("Include Dedicated Kitchen Circuit", value=True)
            
        with col2:
            st.markdown("**Load Heuristics (Watts per unit)**")
            light_w = st.number_input("Lighting Point (W)", min_value=1, value=20, step=5)
            socket_w = st.number_input("Socket Outlet (W)", min_value=10, value=300, step=50)
            ac_w = st.number_input("AC Unit (W)", min_value=100, value=1500, step=100)
            kitchen_w = st.number_input("Kitchen Load (W)", min_value=500, value=3000, step=500)
            
            st.markdown("**Diversity Factors (0.1 to 1.0)**")
            light_df = st.slider("Lighting Diversity Factor", min_value=0.1, max_value=1.0, value=0.8, step=0.1)
            socket_df = st.slider("Socket Diversity Factor", min_value=0.1, max_value=1.0, value=0.6, step=0.1)

        if st.button("Design Internal Circuits", type="primary"):
            inputs = {
                'num_rooms': num_rooms,
                'num_acs': num_acs,
                'num_lights': num_lights,
                'num_sockets': num_sockets,
                'has_kitchen': has_kitchen
            }
            heuristics = {
                'light_w': light_w,
                'socket_w': socket_w,
                'ac_w': ac_w,
                'kitchen_w': kitchen_w
            }
            diversity = {
                'lighting_df': light_df,
                'socket_df': socket_df,
                'ac_df': 0.9,
                'kitchen_df': 0.8
            }
            
            with st.spinner("Designing circuits..."):
                wiring_data = InternalWiringEngine.design_internal_wiring(inputs, heuristics, diversity)
            
            with st.spinner("Generating AI Explanation..."):
                wiring_explanation = explain_internal_wiring(wiring_data)
                
            st.markdown("---")
            st.subheader("🔌 Circuit Distribution Table")
            
            import pandas as pd
            df = pd.DataFrame(wiring_data['circuits'])
            # Rename columns for display
            df_display = df[['id', 'type', 'power_w', 'current_a', 'cable_size_mm2', 'mcb_a', 'length_m']].copy()
            df_display.columns = ["Circuit ID", "Type", "Power (W)", "Current (A)", "Cable Size (mm²)", "MCB Rating (A)", "Est. Length (m)"]
            
            # Format numbers
            df_display["Current (A)"] = df_display["Current (A)"].apply(lambda x: f"{x:.2f}")
            df_display["Est. Length (m)"] = df_display["Est. Length (m)"].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("📦 Cable Summary & Total Load")
            
            s1, s2 = st.columns(2)
            with s1:
                st.markdown("**Estimated Total Loads:**")
                st.write(f"- **Raw Connected Load:** {wiring_data['summary']['total_power_w']:.0f} W")
                st.write(f"- **Diversified Load:** {wiring_data['summary']['total_power_diversified_w']:.0f} W")
            
            with s2:
                st.markdown("**Cable Length Requirements:**")
                for size, length in wiring_data['summary']['cable_totals'].items():
                    if size != -1:
                        st.write(f"- **{size} mm²:** {length:.1f} meters")
                    else:
                        st.write(f"- **Warning:** {length:.1f} meters of cable could not be sized correctly.")
                        
            st.markdown("---")
            st.subheader("🤖 AI Wiring Insight")
            st.info(wiring_explanation)

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #aaa; font-size: 0.8rem;'>© 2025 SpecSense AI | Graduation Project Team</div>", unsafe_allow_html=True)
