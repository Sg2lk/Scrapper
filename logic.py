import cloudscraper
from bs4 import BeautifulSoup
import re
import json
import time
import random
import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_TELEGRAM = os.getenv("TELEGRAM_CHAT_ID")

def conectar_db():
    return sqlite3.connect('precios.db')

def enviar_alerta_telegram(nombre, precio_antiguo, precio_nuevo, url, tienda):
    if not TOKEN_TELEGRAM or not CHAT_ID_TELEGRAM:
        return
        
    mensaje = (
        f"🚨 *¡BAJADA DE PRECIO en {tienda}!*\n\n"
        f"📦 {nombre}\n"
        f"📉 Antes: {precio_antiguo}€\n"
        f"✅ *Ahora: {precio_nuevo}€*\n\n"
        f"🔗 [Ver producto]({url})"
    )
    url_api = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    try:
        requests.post(url_api, json={"chat_id": CHAT_ID_TELEGRAM, "text": mensaje, "parse_mode": "Markdown"})
    except:
        pass

def limpiar_precio(texto):
    if not texto: return 0.0
    texto = str(texto).replace('€', '').replace('\xa0', '').strip()
    limpio = re.sub(r'[^\d.,]', '', texto)
    if ',' in limpio and '.' in limpio:
        if limpio.rfind('.') > limpio.rfind(','): limpio = limpio.replace(',', '')
        else: limpio = limpio.replace('.', '').replace(',', '.')
    elif ',' in limpio: limpio = limpio.replace(',', '.')
    try:
        val = float(limpio)
        return val if val > 0.01 else 0.0
    except: return 0.0

def extraer_datos_universales(soup):
    datos = {"nombre": None, "precio": None}
    scripts = soup.find_all("script", type="application/ld+json")
    for s in scripts:
        try:
            if not s.string: continue
            raw_data = json.loads(s.string)
            def buscar_recursivo(obj):
                if isinstance(obj, dict):
                    obj_min = {str(k).lower(): v for k, v in obj.items()}
                    p = obj_min.get("price") or obj_min.get("priceamount")
                    if not p and "offers" in obj_min:
                        off = obj_min["offers"]
                        if isinstance(off, dict): p = off.get("price")
                        elif isinstance(off, list) and len(off) > 0: p = off[0].get("price")
                    if p and not datos["precio"]:
                        if limpiar_precio(p) > 0.1: datos["precio"] = p
                    n = obj_min.get("name") or obj_min.get("headline")
                    if n and not datos["nombre"]:
                        tipo = str(obj_min.get("@type", "")).lower()
                        if any(x in tipo for x in ["product", "book", "offer", "article"]): datos["nombre"] = n
                    for v in obj.values():
                        if datos["precio"] and datos["nombre"]: return
                        buscar_recursivo(v)
                elif isinstance(obj, list):
                    for item in obj:
                        if datos["precio"] and datos["nombre"]: return
                        buscar_recursivo(item)
            buscar_recursivo(raw_data)
        except: continue
    if not datos["precio"]:
        meta_p = soup.find(attrs={"itemprop": "price"}) or soup.find("meta", {"property": "product:price:amount"})
        if meta_p: datos["precio"] = meta_p.get("content") or meta_p.get_text()
    if not datos["nombre"]:
        h1 = soup.find("h1")
        if h1: datos["nombre"] = h1.get_text(strip=True)
    return datos

def guardar_en_db(nombre, url, precio_sucio, tienda):
    precio_final = limpiar_precio(precio_sucio)
    if precio_final <= 0: return False
    nombre_limpio = re.split(r' [|] | - | · | – | \n', nombre)[0].strip()
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    try:
        cursor.execute('SELECT id FROM productos WHERE url = ?', (url,))
        res_p = cursor.fetchone()
        if not res_p:
            cursor.execute('INSERT INTO productos (nombre, url, tienda) VALUES (?, ?, ?)', (nombre_limpio, url, tienda))
            producto_id = cursor.lastrowid
            ultimo_precio = None
        else:
            producto_id = res_p[0]
            cursor.execute('SELECT precio FROM historial WHERE producto_id = ? ORDER BY fecha DESC LIMIT 1', (producto_id,))
            res_h = cursor.fetchone()
            ultimo_precio = res_h[0] if res_h else None

        if ultimo_precio is None or abs(precio_final - ultimo_precio) > 0.01:
            cursor.execute('INSERT INTO historial (producto_id, precio) VALUES (?, ?)', (producto_id, precio_final))
            conexion.commit()
            if ultimo_precio and precio_final < ultimo_precio:
                enviar_alerta_telegram(nombre_limpio, ultimo_precio, precio_final, url, tienda)
            return True
    except:
        pass
    finally:
        conexion.close()
    return False

def ejecutar_scraper(url):
    mis_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    }
    
    try:
        tienda = "Desconocida"
        dominio = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if dominio:
            tienda = dominio.group(1).split('.')[0].capitalize()

        respuesta = requests.get(url, headers=mis_headers, timeout=10)
        
        if respuesta.status_code in [403, 503]:
            return "CAPTCHA/CORTAFUEGOS"
            
        contenido_html = respuesta.text.lower()
        indicadores_bloqueo = ["cloudflare", "captcha", "robot check", "automated access", "disculpe las molestias", "security check"]
        
        if any(indicador in contenido_html for indicador in indicadores_bloqueo):
            return "CAPTCHA/CORTAFUEGOS"
            
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        datos = extraer_datos_universales(sopa)
        
        if not datos["nombre"] or not datos["precio"]:
            return "DOM_INVALIDO"
            
        exito = guardar_en_db(datos["nombre"], url, datos["precio"], tienda)
        return "OK"
        
    except requests.exceptions.ConnectionError:
        return "ERROR_RED"
    except:
        return "DOM_INVALIDO"