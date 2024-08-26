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

def categorize_product(product_name):
    categories = {
        'Limpieza': [
            'Limpiahogar', 'Limpiador', 'Desinfectante', 'Jabón', 'Detergente', 'Desengrasante', 
            'Antibacterial', 'Servilleta', 'Cloro', 'Amoníaco', 'Abrillantador', 'Esponja', 'Limpiacristales', 'Papel'
        ],
        'Vegetales': [
            'Lechuga', 'Tomate', 'Zanahoria', 'Pepino', 'Pimiento', 'Cebolla', 'Ajo', 
            'Calabacín', 'Brócoli', 'Coliflor', 'Espinaca', 'Champiñón', 'Guisante', 'Judía verde', 'Apio', 'Patatas'
        ],
        'Frutas': [
            'Manzana', 'Plátano', 'Naranja', 'Pera', 'Uva', 'Fresa', 'Kiwi', 'Melón', 'Sandía', 
            'Mango', 'Piña', 'Granada', 'Ciruela', 'Cereza', 'Limón', 'Coco', 'Limones'
        ],
        'Bebidas': [
            'Agua', 'Jugo', 'Refresco', 'Cerveza', 'Vino', 'Limonada', 'Té', 'Café', 'Sidra', 
            'Energética', 'Licores', 'Batido', 'Smoothie', 'Agua con gas', 'Agua mineral', 'Bebida', 'Infusión'
        ],
        'Cereales y Granos': [
            'Pan', 'Arroz', 'Pasta', 'Harina'
        ],
        'Condimentos y Salsas': [
            'Azúcar', 'Sal', 'Aceite', 'Salsas', 'Condimentos'
        ],
        'Legumbres y Sopas': [
            'Legumbres', 'Sopa'
        ],
        'Otros Alimentos': [
            'Cereal', 'Tortillas', 'Enlatados'
        ],
        'Dulces': [
            'Chocolate', 'Galletas', 'Caramelos', 'Chicles', 'Pasteles', 'Bizcochos', 
            'Dulces', 'Helado', 'Bombones', 'Chocolatina', 'Gominolas', 'Piruletas'
        ],
        'Lácteos': [
            'Yogur', 'Mantequilla', 'Queso', 'Crema', 'Leche', 'Batido', 'Requesón', 
            'Ricotta', 'Queso crema', 'Yogur griego', 'Kefir', 'Cuajada', 'Huevos', 'Huevo', 'Natillas'
        ],
        'Carnes': [
            'Pollo', 'Carne de res', 'Cerdo', 'Pescado', 'Salchichas', 'Hamburguesa', 
            'Pechuga', 'Costillas', 'Chorizo', 'Bacon', 'Ternasco', 'Cordero', 'Atún', 'Mariscos', 'Solomillo', 'Solomillos', 'Salmón'
        ],
        'Congelados': [
            'Pizzas', 'Helados', 'Vegetales congelados', 'Comida rápida', 'Bocadillos', 
            'Ultracongelado', 'Ultracongelados', 'Pescado congelado', 'Croquetas', 'Empanadas', 'Ultracongeladas', 'Ultracongelado'
        ],
        'Panadería': [
            'Pan', 'Bollos', 'Croissants', 'Bagels', 'Pan integral', 'Pan de molde', 
            'Pan de centeno', 'Pan de pita', 'Panecillos', 'Baguette', 'Pan de ajo'
        ],
        'Otros': [
            'Paño de cocina', 'Especias', 'Aceite esencial', 'Cinta adhesiva', 'Detergente de lavavajillas', 
            'Baterías', 'Papel higiénico', 'Servilletas', 'Bolsa de basura', 'Aspiradora', 'Pilates'
        ]  # Para productos que no encajan en las categorías anteriores
    }

    # Ordenar las categorías por longitud de los nombres de producto en orden descendente
    sorted_categories = sorted(categories.items(), key=lambda item: -max(len(keyword) for keyword in item[1]))
    
    # Recorre las categorías y sus palabras clave
    for category, keywords in sorted_categories:
        if any(keyword.lower() in product_name.lower() for keyword in keywords):
            return category
    return 'Otros'
    
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

# Contenido de la primera columna (subida de archivos y datos)
with col1:
    st.header("Sube tu PDF")
    uploaded_file = st.file_uploader("Selecciona un ticket PDF", type="pdf")

    if uploaded_file is not None:
        # Guardar el archivo PDF cargado en el directorio PDF
        pdf_path = os.path.join('PDF', uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.success(f"Archivo guardado en {pdf_path}")

        # Extraer texto del PDF cargado
        text = extract_text_from_pdf(uploaded_file)
        
        # Mostrar el texto extraído para depuración (opcional)
        st.write("## Texto Extraído")
        st.text_area("Texto Extraído", text, height=300)

        # Analizar el texto en un DataFrame
        df = parse_text_to_dataframe(text)
        
        if not df.empty:
            # Mostrar el DataFrame
            st.write("## Datos Extraídos")
            st.dataframe(df)

# Contenido de la segunda columna (métricas y gráficos)
with col2:
    if uploaded_file is not None and not df.empty:
        # Calcular métricas
        total_ventas = df['Total Ventas'].sum()
        cantidad_total = df['Cantidad'].sum()
        ingresos_totales = df['PVP Total'].sum()
        precio_medio_item = df['PVP Unitario'].mean()
        productos_hacendado = df['Es Hacendado'].sum()

        # Mostrar métricas en una sola fila
        metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)
        with metrics_col1:
            st.metric("Total Ventas", f"€{total_ventas:,.2f}")
        with metrics_col2:
            st.metric("Cantidad Total", f"{cantidad_total}")
        with metrics_col3:
            st.metric("Ingresos Totales", f"€{ingresos_totales:,.2f}")
        with metrics_col4:
            st.metric("Precio Medio por Item", f"€{precio_medio_item:,.2f}")
        with metrics_col5:
            st.metric("Productos Hacendado", f"{productos_hacendado}")

                # Mostrar gráficos
        st.write("## Análisis de Datos")
        fig1 = px.bar(df, x='Nombre Producto', y='PVP Total', color='Categoría', title='PVP Total por Producto')
        st.plotly_chart(fig1)

        fig2 = px.pie(df, names='Categoría', values='PVP Total', title='Distribución de Gastos por Categoría')
        st.plotly_chart(fig2)
