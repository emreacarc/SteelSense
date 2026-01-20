"""
Streamlit application for SteelSense - Steel Surface Inspection System.
"""

import streamlit as st
import pandas as pd
from PIL import Image
import os
import random
import glob
import logging
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.pdfgen import canvas
from src import SteelDefectDetector
from src.config import DEFAULT_CONF_THRESHOLD, BEST_MODEL_PATH, DATASET_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Steel Surface Inspection System",
    layout="wide"
)

# Custom CSS for sidebar width and dark mode
dark_mode_css = """
<style>
    section[data-testid="stSidebar"] {
        width: 14.29% !important;
        min-width: 14.29% !important;
        max-width: 14.29% !important;
    }
    [data-testid="stSidebar"] {
        width: 14.29% !important;
    }
    .main .block-container {
        padding-left: 15%;
    }
"""
dark_mode_css += """
    /* Dark mode styles */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stApp header {
        background-color: #0e1117;
    }
    .stApp [data-baseweb="modal"] {
        background-color: #0e1117;
    }
    .main .block-container {
        background-color: #0e1117;
        color: #ffffff;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    .stMarkdown {
        color: #ffffff;
    }
    .stMarkdown p {
        color: #ffffff;
    }
    .stDataFrame {
        background-color: #262730;
    }
    .stDataFrame table {
        background-color: #262730;
        color: #ffffff;
    }
    .stDataFrame th {
        background-color: #1e3a5f;
        color: #ffffff;
    }
    .stDataFrame td {
        color: #ffffff;
    }
    .stButton > button {
        background-color: #1e3a5f;
        color: #ffffff;
        border: 1px solid #2c5282;
    }
    .stButton > button:hover {
        background-color: #2c5282;
        color: #ffffff;
    }
    .stButton > button[kind="primary"] {
        background-color: #1e3a5f;
        color: #ffffff;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2c5282;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
    }
    .stNumberInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
    }
    .stSelectbox > div > div > select {
        background-color: #262730;
        color: #ffffff;
    }
    .stFileUploader > div {
        background-color: #000000 !important;
    }
    .stFileUploader button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }
    .stFileUploader button:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    .stFileUploader label {
        color: #ffffff !important;
    }
    /* File uploader placeholder and info text - black */
    .stFileUploader p {
        color: #000000 !important;
    }
    .stFileUploader [data-testid="stFileUploader"] p {
        color: #000000 !important;
    }
    .stFileUploader span {
        color: #000000 !important;
    }
    .stFileUploader [data-testid="stFileUploader"] span {
        color: #000000 !important;
    }
    .stFileUploader [data-testid="stFileUploader"] * {
        color: #000000 !important;
    }
    /* Keep button text white */
    .stFileUploader button {
        color: #ffffff !important;
    }
    .stFileUploader button * {
        color: #ffffff !important;
    }
    .stInfo {
        background-color: #1e3a5f !important;
        color: #ffffff !important;
        opacity: 1 !important;
        border: 1px solid #2c5282 !important;
    }
    .stInfo > div {
        background-color: #1e3a5f !important;
        opacity: 1 !important;
    }
    .stInfo * {
        color: #ffffff !important;
    }
    .stInfo p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stInfo [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    .stInfo [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stInfo svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    .stInfo [data-testid="stIcon"] {
        color: #ffffff !important;
    }
    .stSuccess {
        background-color: #1e3a5f !important;
        color: #ffffff !important;
        border: 1px solid #2c5282 !important;
    }
    .stSuccess * {
        color: #ffffff !important;
    }
    .stSuccess p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stSuccess [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    .stSuccess [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stWarning {
        background-color: #1e3a5f !important;
        color: #ffffff !important;
        border: 1px solid #2c5282 !important;
    }
    .stWarning * {
        color: #ffffff !important;
    }
    .stWarning p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stWarning [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    .stWarning [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stError {
        background-color: #721c24 !important;
        color: #ffffff !important;
        border: 1px solid #8b2635 !important;
    }
    .stError * {
        color: #ffffff !important;
    }
    .stError p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stError [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    .stError [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0e1117;
    }
    /* Sidebar text colors */
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] p {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] a {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #ffffff !important;
    }
    /* Text input colors */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #a0a0a0 !important;
    }
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: #ffffff !important;
    }
    .stTextArea > div > div > textarea::placeholder {
        color: #a0a0a0 !important;
    }
    .stNumberInput > div > div > input {
        background-color: #262730;
        color: #ffffff !important;
    }
    .stSelectbox > div > div > select {
        background-color: #262730;
        color: #ffffff !important;
    }
    .stSelectbox > div > div > select option {
        background-color: #262730;
        color: #ffffff !important;
    }
    .stRadio > label {
        color: #ffffff !important;
    }
    .stCheckbox > label {
        color: #ffffff !important;
    }
    /* All form element labels */
    label {
        color: #ffffff !important;
    }
    .stSlider > label {
        color: #ffffff !important;
    }
    .stSlider label {
        color: #ffffff !important;
    }
    .stFileUploader > label {
        color: #ffffff !important;
    }
    .stFileUploader label {
        color: #ffffff !important;
    }
    .stTextInput > label {
        color: #ffffff !important;
    }
    .stTextInput label {
        color: #ffffff !important;
    }
    .stNumberInput > label {
        color: #ffffff !important;
    }
    .stNumberInput label {
        color: #ffffff !important;
    }
    .stSelectbox > label {
        color: #ffffff !important;
    }
    .stSelectbox label {
        color: #ffffff !important;
    }
    .stTextArea > label {
        color: #ffffff !important;
    }
    .stTextArea label {
        color: #ffffff !important;
    }
    /* Help text */
    .stTooltip,
    .stTooltip * {
        color: #ffffff !important;
    }
    [data-testid="stTooltipIcon"] {
        color: #ffffff !important;
    }
    /* Sidebar button colors */
    section[data-testid="stSidebar"] .stButton > button {
        color: #ffffff !important;
    }
    /* Sidebar selectbox colors */
    section[data-testid="stSidebar"] .stSelectbox > div > div > select {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
    }
</style>
"""
st.markdown(dark_mode_css, unsafe_allow_html=True)

# Initialize session state
if "detector" not in st.session_state:
    st.session_state.detector = None
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Single Inspection"
if "conf_threshold" not in st.session_state:
    st.session_state.conf_threshold = DEFAULT_CONF_THRESHOLD
if "batch_results" not in st.session_state:
    st.session_state.batch_results = []
if "show_detailed_results" not in st.session_state:
    st.session_state.show_detailed_results = False
if "show_images" not in st.session_state:
    st.session_state.show_images = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


def load_detector():
    """Load the defect detector model."""
    if st.session_state.detector is None:
        st.session_state.detector = SteelDefectDetector()
    
    if not st.session_state.model_loaded:
        try:
            st.session_state.detector.load_model()
            st.session_state.model_loaded = True
            return True
        except FileNotFoundError as e:
            st.error(f"Model file not found: {str(e)}")
            return False
        except ImportError as e:
            st.error(f"Import error: {str(e)}")
            st.info("Please ensure all required packages are installed. Check the requirements.txt file.")
            return False
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    return True


def generate_pdf_report(batch_results, conf_threshold, sorted_images, defect_counts, detector, uploaded_files=None, random_batch_images=None):
    """Generate PDF report for batch inspection results."""
    buffer = BytesIO()
    
    # Footer function
    def add_footer(canvas, doc):
        """Add footer with text and page number to each page."""
        canvas.saveState()
        
        # Footer text
        footer_text = "Generated with SteelSense App | Emre Açar"
        footer_font_size = 8
        
        # Get page dimensions
        page_width = A4[0]
        page_height = A4[1]
        
        # Footer position (0.5 inch from bottom)
        footer_y = 0.5 * inch
        
        # Draw footer text (left aligned)
        canvas.setFont("Helvetica", footer_font_size)
        canvas.setFillColor(colors.grey)
        canvas.drawString(0.5 * inch, footer_y, footer_text)
        
        # Draw page number (right aligned)
        page_num = canvas.getPageNumber()
        page_text = f"Page {page_num}"
        text_width = canvas.stringWidth(page_text, "Helvetica", footer_font_size)
        canvas.drawString(page_width - 0.5 * inch - text_width, footer_y, page_text)
        
        canvas.restoreState()
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=0.5*inch, 
        bottomMargin=0.8*inch,  # Increased to make room for footer
        leftMargin=0.5*inch, 
        rightMargin=0.5*inch,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=12,
        alignment=0  # Left
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Date and time
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<b>Report Date:</b> {date_str}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Report title
    story.append(Paragraph("Steel Surface Inspection Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Batch Inspection Results Table
    story.append(Paragraph("Batch Inspection Results", heading_style))
    
    summary_data = []
    for image_name, img_id in sorted_images:
        defects_in_image = [r for r in batch_results 
                          if r.get('image_name') == image_name 
                          and r.get('class_name') != 'Summary'
                          and r.get('confidence', 0) >= conf_threshold]
        
        defect_types = {}
        for defect in defects_in_image:
            defect_type = defect.get('class_name', 'Unknown')
            defect_types[defect_type] = defect_types.get(defect_type, 0) + 1
        
        summary_data.append([
            str(img_id),
            image_name[:30] + '...' if len(image_name) > 30 else image_name,
            str(len(defects_in_image)),
            ', '.join([f"{k}: {v}" for k, v in defect_types.items()]) if defect_types else 'None'
        ])
    
    if summary_data:
        summary_table = Table([['Image ID', 'Image Name', 'Total Defects', 'Defect Types']] + summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Detailed Results Table
    story.append(Paragraph("Detailed Results", heading_style))
    
    detailed_results = [r for r in batch_results 
                      if r.get('class_name') != 'Summary'
                      and r.get('confidence', 0) >= conf_threshold]
    
    if detailed_results:
        detailed_data = []
        for r in detailed_results:
            detailed_data.append([
                r.get('defect_id', 'N/A'),
                r.get('image_name', 'N/A')[:25] + '...' if len(r.get('image_name', '')) > 25 else r.get('image_name', 'N/A'),
                r.get('class_name', 'N/A'),
                f"{r.get('confidence', 0):.2%}"
            ])
        
        detailed_table = Table([['Image & Defect ID', 'Image Name', 'Class Name', 'Confidence Score']] + detailed_data)
        detailed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(detailed_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Images section
    story.append(Paragraph("Processed Images", heading_style))
    
    for image_name, img_id in sorted_images:
        story.append(Paragraph(f"<b>Image ID: {img_id} - {image_name}</b>", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Get image
        image = None
        if uploaded_files:
            for uf in uploaded_files:
                if uf.name == image_name:
                    image = Image.open(uf)
                    break
        
        if image is None and random_batch_images:
            for path in random_batch_images:
                if os.path.basename(path) == image_name:
                    if os.path.exists(path):
                        image = Image.open(path)
                        break
        
        if image is None:
            train_path = os.path.join(DATASET_DIR, "train", "images", image_name)
            valid_path = os.path.join(DATASET_DIR, "valid", "images", image_name)
            if os.path.exists(train_path):
                image = Image.open(train_path)
            elif os.path.exists(valid_path):
                image = Image.open(valid_path)
        
        if image:
            # Resize images to fit side by side (each ~3 inches wide, max height ~4 inches)
            img_width, img_height = image.size
            max_width_per_image = 3 * inch
            max_height = 4 * inch
            
            # Calculate scaling to fit within max dimensions
            width_ratio = max_width_per_image / img_width if img_width > max_width_per_image else 1
            height_ratio = max_height / img_height if img_height > max_height else 1
            ratio = min(width_ratio, height_ratio)
            
            if ratio < 1:
                new_width = img_width * ratio
                new_height = img_height * ratio
                image = image.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
            
            # Save original image to BytesIO
            img_buffer = BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            rl_img = RLImage(img_buffer, width=image.width, height=image.height)
            
            # Processed image
            rl_proc_img = None
            if detector:
                try:
                    processed_image, _ = detector.predict(image, conf_threshold=conf_threshold)
                    
                    # Resize processed image to match original size
                    proc_width, proc_height = processed_image.size
                    if proc_width != image.width or proc_height != image.height:
                        processed_image = processed_image.resize((image.width, image.height), Image.Resampling.LANCZOS)
                    
                    proc_buffer = BytesIO()
                    processed_image.save(proc_buffer, format='PNG')
                    proc_buffer.seek(0)
                    rl_proc_img = RLImage(proc_buffer, width=processed_image.width, height=processed_image.height)
                except:
                    pass
            
            # Create side-by-side layout using Table
            if rl_proc_img:
                # Both images available - show side by side
                image_table_data = [
                    [
                        Paragraph("<b>Original Image</b>", styles['Normal']),
                        Paragraph("<b>Analysis Results</b>", styles['Normal'])
                    ],
                    [rl_img, rl_proc_img]
                ]
            else:
                # Only original image available
                image_table_data = [
                    [Paragraph("<b>Original Image</b>", styles['Normal']), ""],
                    [rl_img, ""]
                ]
            
            image_table = Table(image_table_data, colWidths=[3.2*inch, 3.2*inch])
            image_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(image_table)
            story.append(Spacer(1, 0.1*inch))
        
        # Defects table for this image
        defects_in_image = [r for r in batch_results 
                          if r.get('image_name') == image_name 
                          and r.get('class_name') != 'Summary'
                          and r.get('confidence', 0) >= conf_threshold]
        
        if defects_in_image:
            story.append(Paragraph("<b>Defects Detected</b>", styles['Normal']))
            defect_data = []
            for defect in defects_in_image:
                defect_data.append([
                    defect.get('defect_id', 'N/A'),
                    defect.get('class_name', 'N/A'),
                    f"{defect.get('confidence', 0):.2%}"
                ])
            
            defect_table = Table([['Defect ID', 'Class Name', 'Confidence Score']] + defect_data)
            defect_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(defect_table)
        else:
            story.append(Paragraph("<i>No defects detected.</i>", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
    
    # Summary Statistics
    story.append(Paragraph("Summary Statistics", heading_style))
    
    total_images = len(sorted_images)
    total_defects = sum(defect_counts.values())
    images_with_defects = sum(1 for count in defect_counts.values() if count > 0)
    images_without_defects = total_images - images_with_defects
    
    story.append(Paragraph(f"<b>Analysis Threshold:</b> {conf_threshold:.2f}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    stats_data = [
        ['Total Images', str(total_images)],
        ['Images with Defects', f"{images_with_defects} ({images_with_defects/total_images*100:.1f}%)" if total_images > 0 else "0"],
        ['Images without Defects', f"{images_without_defects} ({images_without_defects/total_images*100:.1f}%)" if total_images > 0 else "0"],
        ['Total Defects', str(total_defects)]
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Defect distribution
    defect_distribution = {}
    for r in batch_results:
        if r.get('class_name') != 'Summary' and r.get('confidence', 0) >= conf_threshold:
            defect_type = r.get('class_name', 'Unknown')
            defect_distribution[defect_type] = defect_distribution.get(defect_type, 0) + 1
    
    if defect_distribution:
        story.append(Paragraph("<b>Defect Distribution</b>", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        dist_data = [['Defect Type', 'Count', 'Percentage']]
        for defect_type, count in sorted(defect_distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_defects * 100) if total_defects > 0 else 0
            dist_data.append([defect_type, str(count), f"{percentage:.2f}%"])
        
        dist_table = Table(dist_data)
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(dist_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def get_random_images_from_dataset(count=1, conf_threshold=0.20, require_defects=True):
    """Get random images from dataset. Only returns images with defects if require_defects=True."""
    all_images = []
    
    # Get images from train and valid directories
    train_images_dir = os.path.join(DATASET_DIR, "train", "images")
    valid_images_dir = os.path.join(DATASET_DIR, "valid", "images")
    
    if os.path.exists(train_images_dir):
        train_images = glob.glob(os.path.join(train_images_dir, "*.jpg")) + \
                      glob.glob(os.path.join(train_images_dir, "*.jpeg")) + \
                      glob.glob(os.path.join(train_images_dir, "*.png"))
        all_images.extend(train_images)
    
    if os.path.exists(valid_images_dir):
        valid_images = glob.glob(os.path.join(valid_images_dir, "*.jpg")) + \
                      glob.glob(os.path.join(valid_images_dir, "*.jpeg")) + \
                      glob.glob(os.path.join(valid_images_dir, "*.png"))
        all_images.extend(valid_images)
    
    if not all_images:
        return []
    
    # If defects are required, filter images
    if require_defects:
        # Use existing detector from session state or create new one
        if st.session_state.detector is None or not st.session_state.model_loaded:
            # Try to load detector
            if not load_detector():
                # If model not found or import error, return random images without filtering
                selected_count = min(count, len(all_images))
                return random.sample(all_images, selected_count)
        
        detector = st.session_state.detector
        
        # Shuffle images for random selection
        random.shuffle(all_images)
        
        images_with_defects = []
        max_attempts = min(len(all_images), count * 50)  # Try up to 50x the requested count to find images with defects above threshold
        
        for image_path in all_images[:max_attempts]:
            if len(images_with_defects) >= count:
                break
            
            try:
                image = Image.open(image_path)
                _, detection_data = detector.predict(
                    image,
                    conf_threshold=conf_threshold
                )
                
                # Only add if defects are found above the confidence threshold
                # detection_data already contains only defects above threshold (filtered by predict function)
                if detection_data and len(detection_data) > 0:
                    images_with_defects.append(image_path)
            except ImportError as e:
                # If import error occurs during prediction, log and skip
                logger.warning(f"Import error during prediction: {str(e)}")
                continue
            except Exception as e:
                # Skip images that can't be processed
                logger.debug(f"Error processing image {image_path}: {str(e)}")
                continue
        
        return images_with_defects[:count]
    else:
        # Select random images without filtering
        selected_count = min(count, len(all_images))
        return random.sample(all_images, selected_count)


def single_inspection_page():
    """Single image inspection page."""
    st.header("Single Inspection")
    st.markdown("---")
    col_info_single, col_empty_info_single = st.columns([1, 1])
    with col_info_single:
        st.info("You can either upload and analyze a photo or use the random button to view images from the dataset.")
    
    # Confidence threshold and file uploader - limited to 50% width
    col_main, col_empty = st.columns([1, 1])
    
    with col_main:
        conf_threshold_input = st.number_input(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.conf_threshold,
            step=0.01,
            format="%.2f",
            help="Adjust the confidence threshold for defect detection",
            key="conf_input"
        )
        st.session_state.conf_threshold = conf_threshold_input
        
        uploaded_file = st.file_uploader(
            "Upload a steel surface image for defect detection",
            type=["jpg", "jpeg", "png", "bmp"],
            help="Supported formats: JPG, JPEG, PNG, BMP"
        )
    
    conf_threshold = st.session_state.conf_threshold
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, use_container_width=True)
        
        with col2:
            st.subheader("Analysis Results")
            
            # Load model and perform prediction
            if load_detector():
                with st.spinner("Analyzing surface integrity..."):
                    try:
                        processed_image, detection_data = st.session_state.detector.predict(
                            image,
                            conf_threshold=conf_threshold
                        )
                        
                        # Display processed image
                        st.image(processed_image, use_container_width=True)
                        
                        # Display detection results table
                        if detection_data:
                            st.markdown("### Detection Results")
                            df = pd.DataFrame(detection_data)
                            df_display = df[["class_name", "confidence"]].copy()
                            df_display["confidence"] = df_display["confidence"].apply(
                                lambda x: f"{x:.2%}"
                            )
                            df_display.columns = ["Class Name", "Confidence Score"]
                            st.dataframe(df_display, use_container_width=True, hide_index=True)
                            
                            st.info(f"Total defects detected: {len(detection_data)}")
                        else:
                            st.success("No defects detected. Surface integrity is good.")
                            
                    except Exception as e:
                        st.error(f"Error during prediction: {str(e)}")
            else:
                st.error(
                    "Model not found. Please run `setup.py` to download the dataset and train the model.\n\n"
                    "```bash\n"
                    "python setup.py\n"
                    "```"
                )
    
    else:
        col_info, col_empty3 = st.columns([1, 1])
        with col_info:
            st.info("Please upload an image to begin defect detection analysis.")
    
    # Random image button at the bottom
    st.markdown("---")
    col_btn, col_empty_btn = st.columns([1, 1])
    with col_btn:
        if st.button("Get Random Surface", type="primary", use_container_width=True):
            # Clear previous random image
            if "random_image_path" in st.session_state:
                del st.session_state.random_image_path
            
            random_images = get_random_images_from_dataset(count=1, conf_threshold=conf_threshold, require_defects=True)
            if random_images:
                image_path = random_images[0]
                st.session_state.random_image_path = image_path
                st.rerun()
            else:
                st.warning(f"No images with defects found above confidence threshold ({conf_threshold:.2%}). Try lowering the confidence threshold or check the dataset.")
    
    # Display random image if selected
    if "random_image_path" in st.session_state and os.path.exists(st.session_state.random_image_path):
        image = Image.open(st.session_state.random_image_path)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, use_container_width=True)
        
        with col2:
            st.subheader("Analysis Results")
            
            if load_detector():
                with st.spinner("Analyzing surface integrity..."):
                    try:
                        processed_image, detection_data = st.session_state.detector.predict(
                            image,
                            conf_threshold=conf_threshold
                        )
                        
                        st.image(processed_image, use_container_width=True)
                        
                        if detection_data:
                            st.markdown("### Detection Results")
                            df = pd.DataFrame(detection_data)
                            df_display = df[["class_name", "confidence"]].copy()
                            df_display["confidence"] = df_display["confidence"].apply(
                                lambda x: f"{x:.2%}"
                            )
                            df_display.columns = ["Class Name", "Confidence Score"]
                            st.dataframe(df_display, use_container_width=True, hide_index=True)
                            
                            st.info(f"Total defects detected: {len(detection_data)}")
                        else:
                            st.success("No defects detected. Surface integrity is good.")
                            
                    except Exception as e:
                        st.error(f"Error during prediction: {str(e)}")
            else:
                st.error(
                    "Model not found. Please run `setup.py` to download the dataset and train the model.\n\n"
                    "```bash\n"
                    "python setup.py\n"
                    "```"
                )


def batch_inspection_page():
    """Batch image inspection page."""
    st.header("Batch Inspection")
    st.markdown("---")
    col_info_batch, col_empty_info_batch = st.columns([1, 1])
    with col_info_batch:
        st.info("You can either upload and analyze photos or use the random button to view images from the dataset.")
    
    # File uploader and confidence threshold - limited to 50% width
    col_uploader, col_empty = st.columns([1, 1])
    with col_uploader:
        conf_threshold_input = st.number_input(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.conf_threshold,
            step=0.01,
            format="%.2f",
            help="Adjust the confidence threshold for defect detection",
            key="batch_conf_input"
        )
        st.session_state.conf_threshold = conf_threshold_input
        
        uploaded_files = st.file_uploader(
            "Upload multiple steel surface images for batch analysis",
            type=["jpg", "jpeg", "png", "bmp"],
            accept_multiple_files=True,
            help="Supported formats: JPG, JPEG, PNG, BMP. Select multiple files to process in batch."
        )
    
    conf_threshold = st.session_state.conf_threshold
    
    if uploaded_files:
        if not load_detector():
            st.error(
                "Model not found. Please run `setup.py` to download the dataset and train the model.\n\n"
                "```bash\n"
                "python setup.py\n"
                "```"
            )
        else:
            # Process all images
            col_btn, col_info = st.columns([1, 2])
            with col_btn:
                if st.button("Analyze All Images", type="primary", use_container_width=True):
                    all_results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Assign image_id starting from 1
                    image_id = 1
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing image {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        try:
                            image = Image.open(uploaded_file)
                            processed_image, detection_data = st.session_state.detector.predict(
                                image,
                                conf_threshold=conf_threshold
                            )
                            
                            # Store results with image_id and defect_id
                            defect_letter = 'A'
                            for detection in detection_data:
                                detection['image_name'] = uploaded_file.name
                                detection['image_id'] = image_id
                                detection['defect_id'] = f"{image_id}-{defect_letter}"
                                defect_letter = chr(ord(defect_letter) + 1)  # A -> B -> C, etc.
                            all_results.extend(detection_data)
                            
                            # Increment image_id for next image
                            image_id += 1
                            
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    status_text.text("Analysis complete!")
                    st.session_state.batch_results = all_results
                    st.session_state.batch_images = uploaded_files
            with col_info:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing for alignment
                num_files = len(uploaded_files)
                file_text = "image" if num_files == 1 else "images"
                st.markdown(f"**{num_files} {file_text} selected**")
            
            # Display results if available (from uploaded files)
            has_results = "batch_results" in st.session_state and st.session_state.batch_results and uploaded_files
            if has_results:
                st.markdown("---")
                st.markdown("### Batch Inspection Results")
                
                # Create summary dataframe
                summary_data = []
                image_names = []
                defect_counts = {}
                
                # Get image names from batch_results with their image_id
                unique_images = {}
                for r in st.session_state.batch_results:
                    if r.get('image_name') and r.get('image_id'):
                        image_name = r.get('image_name')
                        image_id = r.get('image_id')
                        if image_name not in unique_images:
                            unique_images[image_name] = image_id
                
                # Sort by image_id
                sorted_images = sorted(unique_images.items(), key=lambda x: x[1])
                
                for image_name, img_id in sorted_images:
                    image_names.append(image_name)
                    
                    # Count defects per image (filter by confidence threshold)
                    defects_in_image = [r for r in st.session_state.batch_results 
                                      if r.get('image_name') == image_name 
                                      and r.get('class_name') != 'Summary'
                                      and r.get('confidence', 0) >= conf_threshold]
                    
                    defect_counts[image_name] = len(defects_in_image)
                    
                    # Group by defect type for this image
                    defect_types = {}
                    for defect in defects_in_image:
                        defect_type = defect.get('class_name', 'Unknown')
                        defect_types[defect_type] = defect_types.get(defect_type, 0) + 1
                    
                    summary_data.append({
                        'Image ID': img_id,
                        'Image Name': image_name,
                        'Total Defects': len(defects_in_image),
                        'Defect Types': ', '.join([f"{k}: {v}" for k, v in defect_types.items()]) if defect_types else 'None'
                    })
                
                summary_df = pd.DataFrame(summary_data)
                # Reorder columns to have Image ID first
                summary_df = summary_df[['Image ID', 'Image Name', 'Total Defects', 'Defect Types']]
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # Custom CSS for dark navy buttons
                st.markdown("""
                <style>
                .stButton > button[kind="primary"] {
                    background-color: #1e3a5f;
                    color: white;
                    border: none;
                }
                .stButton > button[kind="primary"]:hover {
                    background-color: #2c5282;
                    color: white;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col_btn1, col_btn2, col_btn3, col_empty_btn = st.columns([1, 1, 1, 1])
                with col_btn1:
                    if st.button("Show Detailed Results", type="primary", use_container_width=True):
                        st.session_state.show_detailed_results = not st.session_state.show_detailed_results
                with col_btn2:
                    if st.button("Show Images", type="primary", use_container_width=True):
                        st.session_state.show_images = not st.session_state.show_images
                with col_btn3:
                    if st.button("Generate PDF Report", type="primary", use_container_width=True, key="uploaded_pdf_btn"):
                        try:
                            pdf_buffer = generate_pdf_report(
                                st.session_state.batch_results,
                                conf_threshold,
                                sorted_images,
                                defect_counts,
                                st.session_state.detector if st.session_state.model_loaded else None,
                                uploaded_files,
                                None
                            )
                            st.download_button(
                                label="Download PDF Report",
                                data=pdf_buffer,
                                file_name=f"steel_inspection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key="uploaded_download_btn"
                            )
                        except Exception as e:
                            st.error(f"Error generating PDF report: {str(e)}")
                
                # Display detailed results (filter by confidence threshold)
                if st.session_state.show_detailed_results:
                    detailed_results = [r for r in st.session_state.batch_results 
                                      if r.get('class_name') != 'Summary'
                                      and r.get('confidence', 0) >= conf_threshold]
                    
                    if detailed_results:
                        detailed_df = pd.DataFrame(detailed_results)
                        display_df = detailed_df[["defect_id", "image_name", "class_name", "confidence"]].copy()
                        display_df["confidence"] = display_df["confidence"].apply(
                            lambda x: f"{x:.2%}" if isinstance(x, (int, float)) and x <= 1.0 else str(x)
                        )
                        display_df.columns = ["Image & Defect ID", "Image Name", "Class Name", "Confidence Score"]
                        # Reorder columns to have Image & Defect ID first
                        display_df = display_df[["Image & Defect ID", "Image Name", "Class Name", "Confidence Score"]]
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Display images
                if st.session_state.show_images:
                    st.markdown("### Processed Images")
                    for image_name, img_id in sorted_images:
                        st.markdown(f"**Image ID: {img_id} - {image_name}**")
                        col_orig, col_proc = st.columns(2)
                        
                        try:
                            # Find image - could be from uploaded files or random images
                            image = None
                            if uploaded_files:
                                # Find in uploaded files
                                for uf in uploaded_files:
                                    if uf.name == image_name:
                                        image = Image.open(uf)
                                        break
                            
                            if image is None:
                                # Try to find in random_batch_images or dataset
                                image_path = None
                                if "random_batch_images" in st.session_state:
                                    for path in st.session_state.random_batch_images:
                                        if os.path.basename(path) == image_name:
                                            image_path = path
                                            break
                                
                                if image_path and os.path.exists(image_path):
                                    image = Image.open(image_path)
                                else:
                                    # Try to find in dataset
                                    train_path = os.path.join(DATASET_DIR, "train", "images", image_name)
                                    valid_path = os.path.join(DATASET_DIR, "valid", "images", image_name)
                                    if os.path.exists(train_path):
                                        image = Image.open(train_path)
                                    elif os.path.exists(valid_path):
                                        image = Image.open(valid_path)
                                    else:
                                        st.error(f"Image not found: {image_name}")
                                        continue
                            
                            # Get defects for this image (filter by confidence threshold)
                            defects_in_image = [r for r in st.session_state.batch_results 
                                              if r.get('image_name') == image_name 
                                              and r.get('class_name') != 'Summary'
                                              and r.get('confidence', 0) >= conf_threshold]
                            
                            with col_orig:
                                st.subheader("Original Image")
                                st.image(image, use_container_width=True)
                            
                            with col_proc:
                                st.subheader("Analysis Results")
                                # Get processed image with detections
                                processed_image, _ = st.session_state.detector.predict(
                                    image,
                                    conf_threshold=conf_threshold
                                )
                                st.image(processed_image, use_container_width=True)
                                
                                # Display defects for this image
                                if defects_in_image:
                                    st.markdown("#### Defects Detected")
                                    defect_df = pd.DataFrame(defects_in_image)
                                    defect_display = defect_df[["defect_id", "class_name", "confidence"]].copy()
                                    defect_display["confidence"] = defect_display["confidence"].apply(
                                        lambda x: f"{x:.2%}"
                                    )
                                    defect_display.columns = ["Defect ID", "Class Name", "Confidence Score"]
                                    # Reorder columns to have Defect ID first
                                    defect_display = defect_display[["Defect ID", "Class Name", "Confidence Score"]]
                                    st.dataframe(defect_display, use_container_width=True, hide_index=True)
                                    st.info(f"Total defects: {len(defects_in_image)}")
                                else:
                                    st.success("No defects detected.")
                            
                        except Exception as e:
                            st.error(f"Error displaying {image_name}: {str(e)}")
                        st.markdown("---")
                
                # Summary statistics
                total_images = len(sorted_images)
                total_defects = sum(defect_counts.values())
                images_with_defects = sum(1 for count in defect_counts.values() if count > 0)
                images_without_defects = total_images - images_with_defects
                
                # Calculate defect distribution (filter by confidence threshold)
                defect_distribution = {}
                detailed_results = [r for r in st.session_state.batch_results 
                                  if r.get('class_name') != 'Summary'
                                  and r.get('confidence', 0) >= conf_threshold]
                
                for defect in detailed_results:
                    defect_type = defect.get('class_name', 'Unknown')
                    defect_distribution[defect_type] = defect_distribution.get(defect_type, 0) + 1
                
                st.markdown("### Summary Statistics")
                
                # Analysis threshold
                st.markdown(f"**Analysis Threshold:** {conf_threshold:.2f}")
                st.markdown("---")
                
                # Hide arrows in metrics
                st.markdown("""
                <style>
                [data-testid="stMetricDelta"] {
                    display: none;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Metrics
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                with col_stat1:
                    st.metric("Total Images", total_images)
                with col_stat2:
                    st.metric("Total Defects", total_defects)
                with col_stat3:
                    percentage_with = (images_with_defects / total_images * 100) if total_images > 0 else 0
                    st.metric("Images with Defects", f"{images_with_defects}/{total_images} ({percentage_with:.1f}%)")
                with col_stat4:
                    percentage_without = (images_without_defects / total_images * 100) if total_images > 0 else 0
                    st.metric("Images without Defects", f"{images_without_defects}/{total_images} ({percentage_without:.1f}%)")
                
                # Defect distribution table
                if defect_distribution:
                    st.markdown("### Defect Distribution")
                    distribution_data = []
                    for defect_type, count in sorted(defect_distribution.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total_defects * 100) if total_defects > 0 else 0
                        distribution_data.append({
                            'Defect Type': defect_type,
                            'Count': count,
                            'Percentage': f"{percentage:.2f}%"
                        })
                    
                    distribution_df = pd.DataFrame(distribution_data)
                    st.dataframe(distribution_df, use_container_width=True, hide_index=True)
    else:
        col_info, col_empty3 = st.columns([1, 1])
        with col_info:
            st.info("Please upload one or more images to begin batch inspection.")
    
    # Random images button at the bottom
    st.markdown("---")
    col_btn, col_select, col_empty_btn = st.columns([1, 1, 2])
    with col_btn:
        num_random_images = st.selectbox(
            "Number of Random Images",
            [3, 5, 10],
            index=0,
            key="num_random_batch"
        )
    with col_select:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing for alignment
        if st.button("Get Random Surface", type="primary", use_container_width=True):
            # Clear previous random images and results
            if "random_batch_images" in st.session_state:
                del st.session_state.random_batch_images
            if "batch_results" in st.session_state:
                del st.session_state.batch_results
            if "batch_images" in st.session_state:
                del st.session_state.batch_images
            
            random_images = get_random_images_from_dataset(count=num_random_images, conf_threshold=conf_threshold, require_defects=True)
            if random_images:
                st.session_state.random_batch_images = random_images
                st.rerun()
            else:
                st.warning(f"No images with defects found above confidence threshold ({conf_threshold:.2%}). Try lowering the confidence threshold or check the dataset.")
    
    # Display random batch images if selected
    if "random_batch_images" in st.session_state and st.session_state.random_batch_images:
        # Check if results already exist for these images
        needs_processing = True
        if "batch_results" in st.session_state and st.session_state.batch_results:
            # Check if we already processed these images
            existing_image_names = set([r.get('image_name') for r in st.session_state.batch_results if r.get('image_name')])
            current_image_names = set([os.path.basename(p) for p in st.session_state.random_batch_images])
            if existing_image_names == current_image_names:
                needs_processing = False
        
        if needs_processing:
            if not load_detector():
                st.error(
                    "Model not found. Please run `setup.py` to download the dataset and train the model.\n\n"
                    "```bash\n"
                    "python setup.py\n"
                    "```"
                )
            else:
                # Process all random images
                all_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Assign image_id starting from 1
                image_id = 1
                
                for idx, image_path in enumerate(st.session_state.random_batch_images):
                    status_text.text(f"Processing image {idx + 1}/{len(st.session_state.random_batch_images)}: {os.path.basename(image_path)}")
                    
                    try:
                        image = Image.open(image_path)
                        processed_image, detection_data = st.session_state.detector.predict(
                            image,
                            conf_threshold=conf_threshold
                        )
                        
                        # Store results with image_id and defect_id
                        defect_letter = 'A'
                        for detection in detection_data:
                            detection['image_name'] = os.path.basename(image_path)
                            detection['image_id'] = image_id
                            detection['defect_id'] = f"{image_id}-{defect_letter}"
                            defect_letter = chr(ord(defect_letter) + 1)  # A -> B -> C, etc.
                        all_results.extend(detection_data)
                        
                        # Increment image_id for next image
                        image_id += 1
                        
                    except Exception as e:
                        st.error(f"Error processing {os.path.basename(image_path)}: {str(e)}")
                    
                    progress_bar.progress((idx + 1) / len(st.session_state.random_batch_images))
                
                status_text.text("Analysis complete!")
                st.session_state.batch_results = all_results
                # Create file-like objects for compatibility
                class FakeFile:
                    def __init__(self, name):
                        self.name = name
                st.session_state.batch_images = [FakeFile(os.path.basename(p)) for p in st.session_state.random_batch_images]
        
        # Display results for random images (after processing or if already processed)
        if "batch_results" in st.session_state and st.session_state.batch_results:
            # Check if these results are from random images
            if "random_batch_images" in st.session_state:
                st.markdown("---")
                st.markdown("### Batch Inspection Results")
                
                # Create summary dataframe
                summary_data = []
                image_names = []
                defect_counts = {}
                
                # Get image names from batch_results with their image_id
                unique_images = {}
                for r in st.session_state.batch_results:
                    if r.get('image_name') and r.get('image_id'):
                        image_name = r.get('image_name')
                        image_id = r.get('image_id')
                        if image_name not in unique_images:
                            unique_images[image_name] = image_id
                
                # Sort by image_id
                sorted_images = sorted(unique_images.items(), key=lambda x: x[1])
                
                for image_name, img_id in sorted_images:
                    image_names.append(image_name)
                    
                    # Count defects per image (filter by confidence threshold)
                    defects_in_image = [r for r in st.session_state.batch_results 
                                      if r.get('image_name') == image_name 
                                      and r.get('class_name') != 'Summary'
                                      and r.get('confidence', 0) >= conf_threshold]
                    
                    defect_counts[image_name] = len(defects_in_image)
                    
                    # Group by defect type for this image
                    defect_types = {}
                    for defect in defects_in_image:
                        defect_type = defect.get('class_name', 'Unknown')
                        defect_types[defect_type] = defect_types.get(defect_type, 0) + 1
                    
                    summary_data.append({
                        'Image ID': img_id,
                        'Image Name': image_name,
                        'Total Defects': len(defects_in_image),
                        'Defect Types': ', '.join([f"{k}: {v}" for k, v in defect_types.items()]) if defect_types else 'None'
                    })
                
                summary_df = pd.DataFrame(summary_data)
                # Reorder columns to have Image ID first
                summary_df = summary_df[['Image ID', 'Image Name', 'Total Defects', 'Defect Types']]
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # Custom CSS for dark navy buttons
                st.markdown("""
                <style>
                .stButton > button[kind="primary"] {
                    background-color: #1e3a5f;
                    color: white;
                    border: none;
                }
                .stButton > button[kind="primary"]:hover {
                    background-color: #2c5282;
                    color: white;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col_btn1, col_btn2, col_btn3, col_empty_btn = st.columns([1, 1, 1, 1])
                with col_btn1:
                    if st.button("Show Detailed Results", type="primary", use_container_width=True, key="random_detailed_btn"):
                        st.session_state.show_detailed_results = not st.session_state.show_detailed_results
                with col_btn2:
                    if st.button("Show Images", type="primary", use_container_width=True, key="random_images_btn"):
                        st.session_state.show_images = not st.session_state.show_images
                with col_btn3:
                    if st.button("Generate PDF Report", type="primary", use_container_width=True, key="random_pdf_btn"):
                        try:
                            pdf_buffer = generate_pdf_report(
                                st.session_state.batch_results,
                                conf_threshold,
                                sorted_images,
                                defect_counts,
                                st.session_state.detector if st.session_state.model_loaded else None,
                                None,
                                st.session_state.random_batch_images
                            )
                            st.download_button(
                                label="Download PDF Report",
                                data=pdf_buffer,
                                file_name=f"steel_inspection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key="random_download_btn"
                            )
                        except Exception as e:
                            st.error(f"Error generating PDF report: {str(e)}")
                
                # Display detailed results (filter by confidence threshold)
                if st.session_state.show_detailed_results:
                    detailed_results = [r for r in st.session_state.batch_results 
                                      if r.get('class_name') != 'Summary'
                                      and r.get('confidence', 0) >= conf_threshold]
                    
                    if detailed_results:
                        detailed_df = pd.DataFrame(detailed_results)
                        display_df = detailed_df[["defect_id", "image_name", "class_name", "confidence"]].copy()
                        display_df["confidence"] = display_df["confidence"].apply(
                            lambda x: f"{x:.2%}" if isinstance(x, (int, float)) and x <= 1.0 else str(x)
                        )
                        display_df.columns = ["Image & Defect ID", "Image Name", "Class Name", "Confidence Score"]
                        # Reorder columns to have Image & Defect ID first
                        display_df = display_df[["Image & Defect ID", "Image Name", "Class Name", "Confidence Score"]]
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Display images
                if st.session_state.show_images:
                    st.markdown("### Processed Images")
                    for image_name, img_id in sorted_images:
                        st.markdown(f"**Image ID: {img_id} - {image_name}**")
                        col_orig, col_proc = st.columns(2)
                        
                        try:
                            # Find image path from random_batch_images
                            image_path = None
                            for path in st.session_state.random_batch_images:
                                if os.path.basename(path) == image_name:
                                    image_path = path
                                    break
                            
                            if image_path and os.path.exists(image_path):
                                image = Image.open(image_path)
                            else:
                                # Try to find in dataset
                                train_path = os.path.join(DATASET_DIR, "train", "images", image_name)
                                valid_path = os.path.join(DATASET_DIR, "valid", "images", image_name)
                                if os.path.exists(train_path):
                                    image = Image.open(train_path)
                                elif os.path.exists(valid_path):
                                    image = Image.open(valid_path)
                                else:
                                    st.error(f"Image not found: {image_name}")
                                    continue
                            
                            # Get defects for this image (filter by confidence threshold)
                            defects_in_image = [r for r in st.session_state.batch_results 
                                              if r.get('image_name') == image_name 
                                              and r.get('class_name') != 'Summary'
                                              and r.get('confidence', 0) >= conf_threshold]
                            
                            with col_orig:
                                st.subheader("Original Image")
                                st.image(image, use_container_width=True)
                            
                            with col_proc:
                                st.subheader("Analysis Results")
                                # Get processed image with detections
                                processed_image, _ = st.session_state.detector.predict(
                                    image,
                                    conf_threshold=conf_threshold
                                )
                                st.image(processed_image, use_container_width=True)
                                
                                # Display defects for this image
                                if defects_in_image:
                                    st.markdown("#### Defects Detected")
                                    defect_df = pd.DataFrame(defects_in_image)
                                    defect_display = defect_df[["defect_id", "class_name", "confidence"]].copy()
                                    defect_display["confidence"] = defect_display["confidence"].apply(
                                        lambda x: f"{x:.2%}"
                                    )
                                    defect_display.columns = ["Defect ID", "Class Name", "Confidence Score"]
                                    # Reorder columns to have Defect ID first
                                    defect_display = defect_display[["Defect ID", "Class Name", "Confidence Score"]]
                                    st.dataframe(defect_display, use_container_width=True, hide_index=True)
                                    st.info(f"Total defects: {len(defects_in_image)}")
                                else:
                                    st.success("No defects detected.")
                            
                        except Exception as e:
                            st.error(f"Error displaying {image_name}: {str(e)}")
                        st.markdown("---")
                
                # Summary statistics
                total_images = len(sorted_images)
                total_defects = sum(defect_counts.values())
                images_with_defects = sum(1 for count in defect_counts.values() if count > 0)
                images_without_defects = total_images - images_with_defects
                
                # Calculate defect distribution (filter by confidence threshold)
                defect_distribution = {}
                detailed_results = [r for r in st.session_state.batch_results 
                                  if r.get('class_name') != 'Summary'
                                  and r.get('confidence', 0) >= conf_threshold]
                
                for defect in detailed_results:
                    defect_type = defect.get('class_name', 'Unknown')
                    defect_distribution[defect_type] = defect_distribution.get(defect_type, 0) + 1
                
                st.markdown("### Summary Statistics")
                
                # Analysis threshold
                st.markdown(f"**Analysis Threshold:** {conf_threshold:.2f}")
                st.markdown("---")
                
                # Hide arrows in metrics
                st.markdown("""
                <style>
                [data-testid="stMetricDelta"] {
                    display: none;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Metrics
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                with col_stat1:
                    st.metric("Total Images", total_images)
                with col_stat2:
                    st.metric("Total Defects", total_defects)
                with col_stat3:
                    percentage_with = (images_with_defects / total_images * 100) if total_images > 0 else 0
                    st.metric("Images with Defects", f"{images_with_defects}/{total_images} ({percentage_with:.1f}%)")
                with col_stat4:
                    percentage_without = (images_without_defects / total_images * 100) if total_images > 0 else 0
                    st.metric("Images without Defects", f"{images_without_defects}/{total_images} ({percentage_without:.1f}%)")
                
                # Defect distribution table
                if defect_distribution:
                    st.markdown("### Defect Distribution")
                    distribution_data = []
                    for defect_type, count in sorted(defect_distribution.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total_defects * 100) if total_defects > 0 else 0
                        distribution_data.append({
                            'Defect Type': defect_type,
                            'Count': count,
                            'Percentage': f"{percentage:.2f}%"
                        })
                    
                    distribution_df = pd.DataFrame(distribution_data)
                    st.dataframe(distribution_df, use_container_width=True, hide_index=True)


def about_project_page():
    """About Project page."""
    st.header("About Project")
    st.markdown("---")
    
    st.markdown("""
    ### SteelSense - Steel Surface Inspection System
    
    A professional Computer Vision application for automated defect detection on steel surfaces using YOLOv8 deep learning model and Streamlit web interface.
    
    """)
    
    st.markdown("### Key Features")
    st.markdown("""
    - **Single Inspection**: Analyze individual steel surface images with real-time defect detection
    - **Batch Inspection**: Process multiple images simultaneously with comprehensive analysis
    - **Random Image Selection**: Test the system with random images from the dataset (3, 5, or 10 images)
    - **Confidence Threshold Control**: Adjustable detection sensitivity (default: 0.20)
    - **Image & Defect ID System**: Unique identification for each image and defect (e.g., Image ID: 1, Defect ID: 1-A, 1-B)
    - **Detailed Results View**: View all detected defects with confidence scores and defect types
    - **Summary Statistics**: Comprehensive statistics including defect distribution, percentages, and analysis threshold
    - **PDF Report Generation**: Export complete inspection reports in PDF format (A4) with all images, tables, and statistics
    - **Visual Analysis**: Side-by-side comparison of original and processed images with defect annotations
    """)
    
    st.markdown("### Defect Classes")
    st.markdown("""
    The system can detect the following 6 types of steel surface defects:
    
    1. **Crazing**: Fine network of cracks on the surface
    2. **Inclusion**: Non-metallic particles embedded in steel
    3. **Patches**: Localized surface irregularities
    4. **Pitted Surface**: Small holes or depressions
    5. **Rolled-in Scale**: Oxide scale pressed into the surface during rolling
    6. **Scratches**: Linear surface damage marks
    """)
    
    st.markdown("### How to Use")
    st.markdown("""
    #### Single Inspection
    1. Navigate to **Single Inspection** page
    2. Upload a steel surface image or click **Get Random Surface** to test with a random image
    3. Adjust confidence threshold if needed (default: 0.20)
    4. View detection results with bounding boxes, confidence scores, and defect classifications
    
    #### Batch Inspection
    1. Navigate to **Batch Inspection** page
    2. Upload multiple images or use **Get Random Surface** button (select 3, 5, or 10 images)
    3. Click **Analyze All Images** to process all uploaded/selected images
    4. View **Batch Inspection Results** table with Image ID, Image Name, Total Defects, and Defect Types
    5. Use **Show Detailed Results** to see all defects with Image & Defect IDs
    6. Use **Show Images** to view original and processed images side-by-side with defect tables
    7. Review **Summary Statistics** including:
       - Total Images, Total Defects
       - Images with/without Defects (with percentages)
       - Defect Distribution table (count and percentage for each defect type)
       - Analysis Threshold used
    8. Click **Generate PDF Report** to export a comprehensive PDF report
    """)
    
    st.markdown("### Technology Stack")
    st.markdown("""
    - **YOLOv8**: State-of-the-art object detection model (Ultralytics)
    - **Streamlit**: Web application framework for interactive UI
    - **PyTorch**: Deep learning framework
    - **ReportLab**: PDF generation library
    - **PIL/Pillow**: Image processing
    - **Pandas**: Data manipulation and table display
    - **OpenCV**: Computer vision operations
    - **Roboflow**: Dataset management and download
    """)
    
    st.markdown("### Project Structure")
    st.markdown("""
    ```
    SteelSense/
    ├── app.py                 # Main Streamlit application
    ├── config.py              # Configuration settings
    ├── setup.py               # Setup script for dataset and model
    ├── requirements.txt       # Python dependencies
    ├── src/
    │   ├── data_manager.py   # Dataset download from Roboflow
    │   ├── model_trainer.py   # YOLOv8 model training
    │   └── inference_engine.py # Defect detection inference
    ├── models/                # Trained YOLOv8 models
    └── data/                  # Dataset (train/valid splits)
    ```
    """)
    
    st.markdown("### Dataset")
    st.markdown("""
    The project uses the **NEU-DET (Northeastern University Steel Surface Defects Database)** dataset, 
    which is a publicly available dataset for steel surface defect detection. The dataset contains 
    images of steel surfaces with 6 different types of defects.
    
    - **Dataset Name**: NEU-DET (Northeastern University Steel Surface Defects Database)
    - **Source**: Roboflow (processed and formatted for YOLOv8)
    - **Roboflow Project**: steel-surface-defects-5cztc
    - **Defect Classes**: 6 classes (Crazing, Inclusion, Patches, Pitted Surface, Rolled-in Scale, Scratches)
    - **Image Format**: RGB images with annotations in YOLO format
    - **Dataset Split**: Train/Validation splits for model training
    """)
    
    st.markdown("### Model Training & Improvement")
    st.markdown("""
    The model is trained using YOLOv8 architecture on the NEU-DET steel defect dataset.
    
    - **Current Model**: YOLOv8s (small variant), 10 epochs
    - **Input Image Size**: 640x640 pixels
    
    **Model Improvements**:
    - Upgraded from YOLOv8n (nano) to YOLOv8s (small) for better accuracy
    - Increased training epochs from 5 to 10
    - Moved from Google Colab to local CPU-based training for stability
    """)


# Sidebar
with st.sidebar:
    # Logo and subtitle
    logo_path = os.path.join("logo", "logo.jpg")
    if os.path.exists(logo_path):
        logo_image = Image.open(logo_path)
        st.image(logo_image, use_container_width=True)
    st.markdown('<p style="font-size: 0.85em; margin: 0;">Steel Surface Inspection System</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Page selection
    pages = ["Single Inspection", "Batch Inspection", "About Project"]
    page_index = 0
    if st.session_state.current_page == "Batch Inspection":
        page_index = 1
    elif st.session_state.current_page == "About Project":
        page_index = 2
    
    page = st.radio(
        "Modules",
        pages,
        index=page_index,
        key="page_selector"
    )
    st.session_state.current_page = page
    
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #2A3B50; padding: 5px 12px; border-radius: 8px;">
        <h3 style="color: #ffffff; margin-top: 0; margin-bottom: 5px; font-size: 1.1em; font-weight: bold;">Contact Developer</h3>
        <p style="color: #ffffff; margin: 3px 0; font-size: 0.9em;">Emre AÇAR</p>
        <p style="color: #ffffff; margin: 3px 0; font-size: 0.9em;">
            <a href="https://www.linkedin.com/in/emreacarc/" style="color: #87CEEB; text-decoration: underline;">My LinkedIn Profile</a>
        </p>
        <p style="color: #ffffff; margin: 3px 0; font-size: 0.9em;">ar.emreacar@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area - render selected page
if st.session_state.current_page == "Single Inspection":
    single_inspection_page()
elif st.session_state.current_page == "Batch Inspection":
    batch_inspection_page()
elif st.session_state.current_page == "About Project":
    about_project_page()
