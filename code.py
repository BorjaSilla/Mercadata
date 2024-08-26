import streamlit as st
import PyPDF2
import pandas as pd
import io
import os

# Ensure the PDF directory exists
if not os.path.exists('PDF'):
    os.makedirs('PDF')

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Streamlit app
st.title("PDF Upload and Text Extraction")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file to the PDF directory
    pdf_path = os.path.join('PDF', uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    st.success(f"File saved to {pdf_path}")

    # Extract text from the uploaded PDF
    text = extract_text_from_pdf(uploaded_file)
    
    # Display the extracted text
    st.write("## Extracted Text")
    st.text_area("PDF Content", text, height=300)

    # Optional: Save the extracted text to a DataFrame and display
    data = {'Extracted Text': [text]}
    df = pd.DataFrame(data)
    st.write("## DataFrame")
    st.dataframe(df)

    # Optional: Download the extracted text as a CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='extracted_text.csv',
        mime='text/csv'
    )