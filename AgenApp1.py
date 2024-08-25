import os
from datetime import datetime
import streamlit as st
from PyPDF2 import PdfReader
import openai
import shutil

# Configure directories
UPLOAD_FOLDER = os.path.expanduser('~/Documents/Samples/Uploads')
RESULT_FOLDER = os.path.expanduser('~/Documents/Samples/Result')

# OpenAI API key
# Replace 'your-openai-api-key' with your actual OpenAI API key
openai.api_key = ""

# Create necessary directories if they do not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(RESULT_FOLDER):
    os.makedirs(RESULT_FOLDER)

# Extract text from a PDF file
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Extract customer name using OpenAI's GPT
def extract_customer_name(text):
    response = openai.chat.completions.create(
        
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract the customer's name from the following text:\n\n{text}"}
        ],
        model="gpt-3.5-turbo",
    )
    return response['choices'][0]['message']['content'].strip()

# Streamlit App
st.title("PDF Customer Name Extractor")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Process File"):
        # Save the uploaded file
        upload_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract text and get customer name
        text = extract_text_from_pdf(upload_path)
        customer_name = extract_customer_name(text)
        
        # Format today's date
        today_date = datetime.today().strftime('%Y-%m-%d')
        
        # New file name
        new_filename = f"{customer_name} - {today_date}.pdf"
        result_path = os.path.join(RESULT_FOLDER, new_filename)
        
        # Move and rename the file
        shutil.move(upload_path, result_path)
        
        st.success(f"File saved successfully as {new_filename} in Result folder.")
        st.write("Customer Name:", customer_name)
else:
    st.warning("Please upload a PDF file to process.")