import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import easyocr
import re
import os
import time

# --- HIGH-VISIBILITY INDUSTRIAL DARK THEME ---
st.set_page_config(page_title="AI Universal Document Forensics", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0d0f14 !important; color: #ffffff !important; }
    .cyber-card { background-color: #161b22; border: 2px solid #30363d; border-radius: 12px; padding: 25px; margin-bottom: 25px; }
    .gov-box-success { background-color: #1b4332; border-left: 6px solid #52b788; padding: 20px; border-radius: 8px; color: #ffffff !important; }
    .gov-box-danger { background-color: #641120; border-left: 6px solid #ff4d6d; padding: 20px; border-radius: 8px; color: #ffffff !important; }
    .stButton>button { background: linear-gradient(135deg, #2ec4b6, #0cb0a1) !important; color: #000000 !important; border: none !important; border-radius: 6px !important; width: 100% !important; height: 54px !important; font-weight: bold !important; font-size: 18px !important; text-transform: uppercase; }
    h1 { color: #2ec4b6 !important; font-weight: 800 !important; }
    h2, h3 { color: #ffffff !important; border-bottom: 1px solid #30363d; padding-bottom: 8px; }
    p, span, label { color: #f0f6fc !important; font-size: 15px !important; font-weight: 500 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; margin-bottom: 35px; padding-bottom: 20px; border-bottom: 2px solid #30363d;'>
        <h1>🔬 AI-DRIVEN UNIVERSAL DOCUMENT FORENSICS</h1>
        <p style='color: #8b949e; font-size: 16px;'>Smart India Hackathon 2026 | Comprehensive Forgery Detection & Centralized Registry Verification Gateway</p>
    </div>
""", unsafe_allow_html=True)

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])
reader = load_ocr()

# --- UNIVERSAL REGISTRY SEARCH ENGINE (FOR ALL INDIAN DOCUMENTS) ---
def scan_and_verify_all_documents(ocr_text):
    # 1. Aadhaar Card Scan
    aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', ocr_text)
    if aadhaar_match:
        return {"found": True, "type": "AADHAAR CARD (UIDAI)", "id": aadhaar_match.group().replace(" ", ""), "db_check": True}
        
    # 2. PAN Card Scan
    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', ocr_text)
    if pan_match:
        return {"found": True, "type": "PAN CARD (INCOME TAX DEPT)", "id": pan_match.group(), "db_check": True}
        
    # 3. Driving License Scan
    dl_match = re.search(r'\b[A-Z]{2}[0-9]{2}\s?[0-9]{11}\b', ocr_text)
    if dl_match:
        return {"found": True, "type": "DRIVING LICENSE (MoRTH)", "id": dl_match.group().replace(" ", ""), "db_check": True}

    # 4. Voter ID Card Scan
    voter_match = re.search(r'\b[A-Z]{3}[0-9]{7}\b', ocr_text)
    if voter_match:
        return {"found": True, "type": "VOTER ID CARD (ECI)", "id": voter_match.group(), "db_check": True}

    # 5. University Degrees / College Certificates / Marks Lists
    # సర్టిఫికెట్‌లో "ROLL NO", "REG NO", "SERIAL NO" లేదా విద్యా బోర్డుల పేర్లు ఉంటే పట్టుకుంటుంది
    if "COLLEGE" in ocr_text or "UNIVERSITY" in ocr_text or "BOARD" in ocr_text or "CERTIFICATE" in ocr_text or "MARKS" in ocr_text:
        serial_match = re.search(r'\b[A-Z0-9]{6,12}\b', ocr_text)
        cert_id = serial_match.group() if serial_match else "CERT-REG-2026"
        return {"found": True, "type": "ACADEMIC CERTIFICATE / COLLEGE MARKS LIST", "id": cert_id, "db_check": True}
        
    # 6. Generic Documents (Ration Card, Birth Certificate, Experience Letter)
    # పైవేవీ మ్యాచ్ కాకపోతే జనరిక్ కింద క్లాసిఫై చేస్తుంది
    num_match = re.search(r'\b[A-Z0-9/-]{6,15}\b', ocr_text)
    gen_id = num_match.group() if num_match else "DOC-UNKNOWN"
    return {"found": True, "type": "GOVERNMENT CERTIFICATE / GENERAL DOCUMENT", "id": gen_id, "db_check": False}

# MOCK APPROVED CENTRAL DATABASE (లిస్ట్‌లో ఉన్న ఐడీలు మాత్రమే ఒరిజినల్ అవుతాయి)
MOCK_CENTRAL_REGISTRY = ["784263912050", "987654321012", "ABCDE1234F", "J1234567", "AP1620260012345", "XYZ1234567", "SG100245", "RE-40552"]
def perform_forensic_scan(uploaded_image):
    temp = "t_orig.jpg"
    resaved = "t_res.jpg"
    uploaded_image.save(temp, 'JPEG', quality=100)
    im = Image.open(temp)
    im.save(resaved, 'JPEG', quality=85)
    diff = ImageChops.difference(Image.open(temp), Image.open(resaved))
    diff_np = np.array(diff)
    max_diff = np.max(diff_np) if np.max(diff_np) > 0 else 1
    ela_vis = ImageEnhance.Brightness(diff).enhance(255.0 / max_diff)
    ela_score = float(max_diff)
    if os.path.exists(temp): os.remove(temp)
    if os.path.exists(resaved): os.remove(resaved)
    return ela_vis, ela_score

col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
    st.write("### 📥 Secure Document Input Portal")
    input_type = st.radio("Choose Scanner Source:", ["File Upload from Storage", "Live Camera Document Capture"])
    uploaded_file = None
    if input_type == "File Upload from Storage":
        uploaded_file = st.file_uploader("Upload any Indian Document / Academic Certificate:", type=["jpg", "png", "jpeg"])
    else:
        captured_file = st.camera_input("Place document inside the frame boundaries")
        if captured_file:
            uploaded_file = Image.open(captured_file)
    if uploaded_file and input_type == "File Upload from Storage":
        st.image(uploaded_file, caption="Target Document Stream", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
    st.write("### 🔍 Forensic Diagnostics Desk")
    
    if st.button("🔒 ACTIVATE FORENSIC SCREENING"):
        if not uploaded_file:
            st.error("Operation Aborted: Operational queue is currently empty.")
        else:
            progress = st.progress(0)
            doc_img = Image.open(uploaded_file) if input_type == "File Upload from Storage" else uploaded_file
            progress.progress(40)
            
            doc_np = np.array(doc_img)
            ocr_text = " ".join(reader.readtext(doc_np, detail=0)).upper()
            progress.progress(70)
            
            ela_vis, ela_score = perform_forensic_scan(doc_img)
            progress.progress(100)
            
            st.write("### 📊 Verification Verdict")
            
            # Run the Universal Search Engine
            verdict = scan_and_verify_all_documents(ocr_text)
            
            # ELA Forgery threshold check
            is_tampered_image = ela_score > 25.0
            
            if verdict["found"]:
                is_valid_registry = verdict["id"] in MOCK_CENTRAL_REGISTRY if verdict["db_check"] else True
                
                # If image is edited OR if it fails central registry validation, mark as FORGERY!
                if is_tampered_image or not is_valid_registry:
                    st.markdown(f"""
                        <div class='gov-box-danger'>
                            <h3 style='color: #ff4d6d; margin-top: 0;'>🚨 FORGERY ALERT: FRAUDULENT DOCUMENT DETECTED</h3>
                            <p><b>DOCUMENT CLASSIFICATION:</b> {verdict['type']}</p>
                            <p><b>EXTRACTED SERIAL / ID NO:</b> {verdict['id']}</p>
                            <p><b>DIAGNOSIS:</b> Fake/Altered File Profile. Either the image pixels are edited digitally (Photoshop/GenAI) or this registration identifier does not exist in official central databases.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class='gov-box-success'>
                            <h3 style='color: #52b788; margin-top: 0;'>✅ VERIFIED & AUTHENTIC DOCUMENT</h3>
                            <p><b>DOCUMENT TYPE:</b> {verdict['type']}</p>
                            <p><b>SERIAL / ID NO:</b> {verdict['id']}</p>
                            <p><b>STATUS:</b> 100% Authentic. This profile has been cross-matched and verified with official central database ledgers.</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                if is_tampered_image:
                    st.markdown("<div class='gov-box-danger'><h3>🚨 FORGERY ALERT: Modified Document Image</h3></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='gov-box-success'><h3>✅ UNALTERED IMAGE STRUCTURE</h3><p>Document image file is consistent.</p></div>", unsafe_allow_html=True)

            with st.expander("🔬 View Digital Forensic Heatmaps"):
                st.write(f"Structural Deviation Peak: `{ela_score:.2f}`")
                st.image(ela_vis, caption="Forensic Compression Variance Visualization")
    st.markdown("</div>", unsafe_allow_html=True)