import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import time
import random
from logic import conectar_db, ejecutar_scraper

st.set_page_config(page_title="PriceTracker Pro", layout="wide", page_icon="📈")

def cargar_resumen():
    conn = conectar_db()
    query = """
    SELECT p.nombre, p.tienda, h.precio, h.fecha, p.url
    FROM productos p
    JOIN historial h ON p.id = h.producto_id
    WHERE h.id IN (SELECT MAX(id) FROM historial GROUP BY producto_id)
    ORDER BY h.fecha DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def cargar_historial(nombre_producto):
    conn = conectar_db()
    query = """
    SELECT h.fecha, h.precio 
    FROM historial h
    JOIN productos p ON p.id = h.producto_id
    WHERE p.nombre = ?
    ORDER BY h.fecha ASC
    """
    df = pd.read_sql_query(query, conn, params=(nombre_producto,))
    conn.close()
    return df

st.sidebar.title("Panel de Control")
menu = st.sidebar.radio("Ir a:", ["Dashboard General", "Análisis Detallado", "Añadir Producto"])
st.sidebar.markdown("---")
st.sidebar.write("### Acciones Globales")

if st.sidebar.button("🔄 Actualizar toda la lista"):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM productos")
    urls = [fila[0] for fila in cursor.fetchall()]
    conn.close()

    if urls:
        st.sidebar.info(f"Actualizando {len(urls)} productos...")
        barra_progreso = st.sidebar.progress(0)
        
        for i, url in enumerate(urls):
            ejecutar_scraper(url)
            barra_progreso.progress((i + 1) / len(urls))
            time.sleep(random.uniform(3, 6))
            
        st.sidebar.success("✅ ¡Actualización terminada!")
        st.balloons()
        st.rerun()
    else:
        st.sidebar.warning("No hay productos guardados.")

if menu == "Dashboard General":
    st.title("📊 Resumen de Monitorización")
    df_resumen = cargar_resumen()
    
    if not df_resumen.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Productos", len(df_resumen))
        col2.metric("Tiendas", len(df_resumen['tienda'].unique()))
        col3.metric("Último Rastro", df_resumen['fecha'].max()[:10])
        
        st.write("---")
        st.write("### Precios Actuales")
        
        busqueda = st.text_input("🔍 Buscar por producto o tienda...")
        if busqueda:
            df_resumen = df_resumen[df_resumen['nombre'].str.contains(busqueda, case=False) | 
                                    df_resumen['tienda'].str.contains(busqueda, case=False)]
        
        st.dataframe(df_resumen[['nombre', 'precio', 'tienda', 'fecha']], width='content')
    else:
        st.warning("La base de datos está vacía. Añade un producto primero.")

elif menu == "Análisis Detallado":
    st.title("📈 Evolución Histórica")
    df_resumen = cargar_resumen()
    
    if not df_resumen.empty:
        producto = st.selectbox("Selecciona un producto:", df_resumen['nombre'].unique())
        df_hist = cargar_historial(producto)
        
        fig = px.line(df_hist, x='fecha', y='precio', title=f"Historial de precios: {producto}",
                      markers=True, line_shape="linear", color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig, width='content')
        
        c1, c2, c3 = st.columns(3)
        precio_actual = df_hist['precio'].iloc[-1]
        precio_min = df_hist['precio'].min()
        c1.metric("Precio Actual", f"{precio_actual}€")
        c2.metric("Mínimo Histórico", f"{precio_min}€")
        c3.metric("Máximo Histórico", f"{df_hist['precio'].max()}€")
        
        if precio_actual == precio_min:
            st.success("✨ ¡Este producto está ahora mismo en su precio más bajo!")
    else:
        st.error("No hay datos históricos disponibles.")

elif menu == "Añadir Producto":
    st.title("🔗 Nuevo Producto")
    st.write("Introduce la URL de cualquier tienda soportada para empezar el rastreo.")
    nueva_url = st.text_input("URL del producto:")
    
    if st.button("Añadir y Scrapear"):
        if nueva_url:
            with st.spinner("Analizando web y extrayendo datos..."):
                resultado = ejecutar_scraper(nueva_url)
                
                if resultado == "OK":
                    st.success("¡Producto detectado y guardado con éxito!")
                    st.balloons()
                elif resultado == "CAPTCHA/CORTAFUEGOS":
                    st.error("🛑 **Error de Seguridad (Cortafuegos):** La plataforma de destino (como Amazon/Cloudflare) ha bloqueado la petición automatizada. Se requiere el uso de proxies o mimetismo avanzado.")
                elif resultado == "ERROR_RED":
                    st.error("🌐 **Error de Conexión:** No se ha podido establecer comunicación con el servidor. Revisa tu conexión a internet o el estado de la web.")
                elif resultado == "DOM_INVALIDO":
                    st.error("🧩 **Error de Estructura (DOM):** Se ha accedido a la web pero los selectores HTML no coinciden. La tienda ha cambiado su diseño o la URL no pertenece a un producto soportado.")
                else:
                    st.error("⚠️ **Error Desconocido:** No se pudo procesar la solicitud. Revisa la URL.")
        else:
            st.error("Por favor, introduce una URL.")