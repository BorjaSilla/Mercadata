import streamlit as st
import PyPDF2
import pandas as pd
import plotly.express as px
import os

# Create the PDF directory if it doesn't exist
if not os.path.exists('PDF'):
    os.makedirs('PDF')

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Function to parse extracted text into a DataFrame
def parse_text_to_dataframe(text):
    lines = text.split('\n')
    data = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            product_name = ' '.join(parts[:-3])
            try:
                quantity = int(parts[-3])
            except ValueError:
                st.warning(f"Could not convert quantity '{parts[-3]}' to int")
                quantity = 0
            price_str = parts[-2].replace('$', '').replace(',', '')
            category = parts[-1]
            try:
                price = float(price_str)
            except ValueError:
                st.warning(f"Could not convert price '{price_str}' to float")
                price = 0.0
            data.append([product_name, quantity, price, category])
    
    df = pd.DataFrame(data, columns=['Product Name', 'Quantity', 'Price', 'Category'])
    return df

# Streamlit app
st.title("PDF Ticket Upload and Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF ticket", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file to the PDF directory
    pdf_path = os.path.join('PDF', uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    st.success(f"File saved to {pdf_path}")

    # Extract text from the uploaded PDF
    text = extract_text_from_pdf(uploaded_file)
    
    # Display the raw text for debugging
    st.write("## Raw Extracted Text")
    st.text_area("Raw Text", text, height=300)

    # Parse text into DataFrame
    df = parse_text_to_dataframe(text)
    
    if not df.empty:
        # Display the DataFrame
        st.write("## Extracted Data")
        st.dataframe(df)

        # Display charts
        # Total sales by product
        df['Total Sales'] = df['Quantity'] * df['Price']
        fig1 = px.bar(df, x='Product Name', y='Total Sales', title="Total Sales by Product")
        st.plotly_chart(fig1)

        # Total quantity sold by category
        fig2 = px.bar(df.groupby('Category')['Quantity'].sum().reset_index(),
                      x='Category', y='Quantity', title="Total Quantity Sold by Category")
        st.plotly_chart(fig2)

        # Total revenue by category
        fig3 = px.bar(df.groupby('Category')['Total Sales'].sum().reset_index(),
                      x='Category', y='Total Sales', title="Total Revenue by Category")
        st.plotly_chart(fig3)
    else:
        st.warning("No data found in the PDF. Please check the format of your ticket.")
