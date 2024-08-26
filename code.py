import streamlit as st
import PyPDF2
import pandas as pd
import plotly.express as px
import os
import re

# Crear el directorio PDF si no existe
if not os.path.exists('PDF'):
    os.makedirs('PDF')

# Función para extraer texto de un archivo PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Función para analizar el texto extraído y convertirlo en un DataFrame
def parse_text_to_dataframe(text):
    # Separar el texto en líneas
    lines = text.split('\n')
    data = []
    
    # Expresión regular para capturar el nombre del producto, cantidad y precio
    pattern = re.compile(r'(.+?)\s+(\d+)\s+([\d,]+ €)')
    
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            product_name, quantity_str, price_str = match.groups()
            try:
                quantity = int(quantity_str)
            except ValueError:
                st.warning(f"No se pudo convertir la cantidad '{quantity_str}' a entero")
                quantity = 0
            price = float(price_str.replace(' €', '').replace(',', '.'))
            data.append([product_name, quantity, price])
    
    # Crear el DataFrame
    df = pd.DataFrame(data, columns=['Nombre Producto', 'Cantidad', 'PVP'])
    return df

# Aplicación Streamlit
st.title("Cargar y Analizar Ticket PDF")

# Cargador de archivos
uploaded_file = st.file_uploader("Sube un ticket PDF", type="pdf")

if uploaded_file is not None:
    # Guardar el archivo PDF cargado en el directorio PDF
    pdf_path = os.path.join('PDF', uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    st.success(f"Archivo guardado en {pdf_path}")

    # Extraer texto del PDF cargado
    text = extract_text_from_pdf(uploaded_file)
    
    # Mostrar el texto extraído para depuración
    st.write("## Texto Extraído")
    st.text_area("Texto Extraído", text, height=300)

    # Analizar el texto en un DataFrame
    df = parse_text_to_dataframe(text)
    
    if not df.empty:
        # Mostrar el DataFrame
        st.write("## Datos Extraídos")
        st.dataframe(df)

        # Mostrar gráficos
        # Ventas totales por producto
        df['Total Ventas'] = df['Cantidad'] * df['PVP']
        fig1 = px.bar(df, x='Nombre Producto', y='Total Ventas', title="Ventas Totales por Producto")
        st.plotly_chart(fig1)

        # Cantidad total entregada
        fig2 = px.bar(df.groupby('Nombre Producto')['Cantidad'].sum().reset_index(),
                      x='Nombre Producto', y='Cantidad', title="Cantidad Total Entregada por Producto")
        st.plotly_chart(fig2)

        # Ingresos totales
        fig3 = px.bar(df.groupby('Nombre Producto')['Total Ventas'].sum().reset_index(),
                      x='Nombre Producto', y='Total Ventas', title="Ingresos Totales por Producto")
        st.plotly_chart(fig3)
    else:
        st.warning("No se encontraron datos en el PDF. Por favor, verifica el formato de tu ticket.")

