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

# Función para categorizar productos en base a su nombre
def categorize_product(product_name):
    categories = {
        'Limpieza': [
            'Limpiahogar', 'Limpiador', 'Desinfectante', 'Jabón', 'Detergente', 'Desengrasante', 'Antibacterial'
        ],
        'Vegetales': [
            'Lechuga', 'Tomate', 'Zanahoria', 'Pepino', 'Pimiento', 'Cebolla', 'Ajo', 'Calabacín', 'Brócoli'
        ],
        'Frutas': [
            'Manzana', 'Plátano', 'Naranja', 'Pera', 'Uva', 'Fresa', 'Kiwi', 'Melón', 'Sandía'
        ],
        'Bebidas': [
            'Agua', 'Jugo', 'Refresco', 'Cerveza', 'Vino', 'Limonada', 'Té', 'Café', 'Sidra'
        ],
        'Alimentos': [
            'Pan', 'Arroz', 'Pasta', 'Harina', 'Azúcar', 'Sal', 'Aceite', 'Leche', 'Cereal'
        ],
        'Dulces': [
            'Chocolate', 'Galletas', 'Caramelos', 'Chicles', 'Pasteles', 'Bizcochos', 'Dulces'
        ],
        'Lácteos': [
            'Yogur', 'Mantequilla', 'Queso', 'Crema', 'Leche', 'Batido', 'Requesón'
        ],
        'Carnes': [
            'Pollo', 'Carne de res', 'Cerdo', 'Pescado', 'Salchichas', 'Hamburguesa', 'Pechuga'
        ],
        'Congelados': [
            'Pizzas', 'Helados', 'Vegetales congelados', 'Comida rápida', 'Bocadillos'
        ],
        'Panadería': [
            'Pan', 'Bollos', 'Croissants', 'Bagels', 'Pan integral', 'Pan de molde'
        ],
        'Otros': []  # Para productos que no encajan en las categorías anteriores
    }
    
    # Recorre las categorías y sus palabras clave
    for category, keywords in categories.items():
        if any(keyword.lower() in product_name.lower() for keyword in keywords):
            return category
    return 'Otros'

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
    df = pd.DataFrame(data, columns=['Nombre Producto', 'Cantidad', 'PVP Total'])
    # Calcular el PVP Unitario
    df['PVP Unitario'] = df['PVP Total'] / df['Cantidad']
    # Calcular el Total Ventas
    df['Total Ventas'] = df['Cantidad'] * df['PVP Unitario']
    # Filtrar productos de Hacendado
    df['Es Hacendado'] = df['Nombre Producto'].str.contains('Hacendado', case=False)
    # Agregar la categoría
    df['Categoría'] = df['Nombre Producto'].apply(categorize_product)
    return df

# Configuración de la página de Streamlit
st.set_page_config(page_title="Análisis de Ticket PDF", layout="wide")

# Agregar el logo en la parte superior usando una URL
st.image("https://www.example.com/logo.png", width=200)  # Reemplaza esta URL con la URL real de tu logo

# Crear columnas para la disposición
col1, col2 = st.columns([1, 3])  # La primera columna ocupa 1/4 del espacio, la segunda ocupa 3/4

# Contenido de la primera columna (subida de archivos)
with col1:
    st.header("Sube tu PDF")
    uploaded_file = st.file_uploader("Selecciona un ticket PDF", type="pdf")

# Contenido de la segunda columna (análisis de datos)
with col2:
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

            # Calcular métricas
            total_ventas = df['Total Ventas'].sum()
            cantidad_total = df['Cantidad'].sum()
            ingresos_totales = df['PVP Total'].sum()
            precio_medio_item = df['PVP Unitario'].mean()
            productos_hacendado = df['Es Hacendado'].sum()

            # Mostrar métricas en una sola fila
            col1, col2, col3, col4, col5 = st
