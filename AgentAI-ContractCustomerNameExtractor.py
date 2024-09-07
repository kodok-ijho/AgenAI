import os
from datetime import datetime
import streamlit as st
from PyPDF2 import PdfReader
import openai
import shutil
import re

# Configure directories
UPLOAD_FOLDER = os.path.expanduser('~/Documents/Samples/Uploads')
#RESULT_FOLDER = os.path.expanduser('~/Documents/Samples/Result')
RESULT_FOLDER = os.path.expanduser('./DocumentsResult')

# OpenAI API key
# Replace 'your-openai-api-key' with your actual OpenAI API key
openai.api_key = ""


# Create necessary directories if they do not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(RESULT_FOLDER):
    os.makedirs(RESULT_FOLDER)

def extract_customer_name(input_file):
   # Open and read the PDF file
    with open(input_file, "rb") as f:
        reader = PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

    # Refined prompt for extracting only the customer name
    prompt = f"Extract only the customer name from the following text:\n\n{text}"

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            #model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        

        # Extract the customer name from the first completion
        customer_name = response.choices[0].message.content.strip()
        #customer_name = response.choices[0].message['content'].strip()

        # Additional processing to ensure the output is only the name
        if customer_name.lower().startswith("the customer name"):
            customer_name = customer_name.split("is", 1)[-1].strip()

        # Additional sanity check (optional)
        if len(customer_name.split()) < 2:  # Assuming a customer name has at least 2 words
            raise ValueError("Extracted name seems invalid")
        
    except Exception as e:
        print(f"Error extracting customer name: {e}")
        return None

    return customer_name

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
        customer_name = extract_customer_name(upload_path)

        # Format today's date
        today_date = datetime.today().strftime('%Y-%m-%d')

        # After extracting the customer name, sanitize it before using it as a file name
        if customer_name:
            # Remove invalid characters for filenames (including newline characters, tabs, etc.)
            customer_name = re.sub(r'[<>:"/\\|?*\n\r\t]', '', customer_name)

            # New file name after formatting the date and ensuring it's clean
            new_filename = f"{customer_name.strip()} - {today_date}.pdf"
            result_path = os.path.join(RESULT_FOLDER, new_filename)

            # Move and rename the file
            shutil.move(upload_path, result_path)

            st.success(f"File saved successfully as {new_filename} in Result folder.")
            st.write("Customer Name:", customer_name)
        else:
            st.error("Failed to extract a valid customer name from the PDF.")
else:
    st.warning("Please upload a PDF file to process.")
