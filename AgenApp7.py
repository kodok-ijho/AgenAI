import os
from datetime import datetime
import streamlit as st
from PyPDF2 import PdfReader
import openai
import shutil
import re
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import io

# Configure directories
UPLOAD_FOLDER = os.path.expanduser('~/Documents/Samples/Uploads')
RESULT_FOLDER = os.path.expanduser('./DocumentsResult')

# OpenAI API key
openai.api_key = "sk-xxxxx"  # Replace with your actual API key

# Create necessary directories if they do not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(RESULT_FOLDER):
    os.makedirs(RESULT_FOLDER)

customer_name = ""  # Initialize customer_name with an empty string
doc_type = ""  # Initialize doc_type with a default value

def extract_text_from_image(pdf_file):
    # Open the PDF using PyMuPDF
    pdf_document = fitz.open(pdf_file)
    text = ''

    # Loop through each page and extract the images
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Render page as an image (pixmap)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))  # Convert pixmap to image
        
        # Perform OCR on the image
        text += pytesseract.image_to_string(img)
        
    return text

def extract_customer_name(input_file, ocr=False):
    text = ''
    
    try:
        # Attempt text-based extraction first
        with open(input_file, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        
        # If no text was found, switch to OCR
        if not text.strip():
            st.warning("No text detected in PDF. Attempting OCR...")
            text = extract_text_from_image(input_file)

    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return "Error processing file"

    # Refined prompt for extracting only the customer name and document type
    prompt = f"Extract only the customer name and document type. " \
             f"Answer with template 'Customer name is [CustomerName] and document type is [DocumentType]', " \
             f"fill [DocumentType] only with 'Contract', 'Invoice' or 'Other' from the following text:\n\n{text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the customer name and document type from the response
        prompt_result = response['choices'][0]['message']['content'].strip()
        print(f"API Response: {prompt_result}")  # Debugging tip: Print API response

        # Extract customer name
        if "Customer name is" in prompt_result:
            customer_name = prompt_result.split("Customer name is", 1)[-1].split("and document type", 1)[0].strip()

        # Extract document type
        if "document type is" in prompt_result:
            doc_type = prompt_result.split("document type is", 1)[-1].strip()

        # Sanity check (assuming a valid customer name has at least 2 words)
        if len(customer_name.split()) < 2:  
            raise ValueError("Extracted name seems invalid")

    except Exception as e:
        print(f"Error extracting customer name: {e}")
        customer_name = "Unnamed_Customer"  # Set to default on error

    # Combine customer name and document type for output
    hasil = f"{customer_name} - {doc_type}"
    
    # Remove invalid characters for the filename
    hasil = re.sub(r'[<>:"/\\|?*]', '', hasil)

    return hasil

# Streamlit App
st.title("PDF Customer Name and Document Type Extractor")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Process File"):
        # Save the uploaded file
        upload_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract text and get customer name
        customer_info = extract_customer_name(upload_path)

        # Ensure customer_info is a string
        if not isinstance(customer_info, str):
            customer_info = "Unnamed_Customer"  # Set to default if it's not valid

        # Format today's date
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Remove invalid characters from the name for file naming
        print(customer_info)

        # New file name
        new_filename = f"{customer_info} - {today_date}.pdf"
        result_path = os.path.join(RESULT_FOLDER, new_filename)

        # Move and rename the file
        shutil.move(upload_path, result_path)

        st.success(f"File saved successfully as {new_filename} in Result folder.")
        st.write("Customer Information:", customer_info)
else:
    st.warning("Please upload a PDF file to process.")
