# Scrapper 🚀

[![Python Version](https://img.shields.io/badge/python-3.10%20%2C%203.11-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/database-SQLite3-003B57.svg)](https://www.sqlite.org/)
[![Code Style](https://img.shields.io/badge/code%20style-clean--code-informational.svg)](https://en.wikipedia.org/wiki/Robert_Cecil_Martin)

**Scrapper** es una solución de ingeniería de software orientada a la automatización, monitorización y análisis del histórico de precios en plataformas de comercio electrónico. La aplicación combina técnicas avanzadas de *web scraping*, almacenamiento relacional local y una interfaz web interactiva para ofrecer un panel de control centralizado y un sistema de alertas en tiempo real.

---

## 🎯 Características Principales

*   **Motor de Scraping Robusto:** Extracción automatizada de información comercial evitando la volatilidad del DOM HTML mediante el análisis de metadatos estructurados.
*   **Histórico e Interfaz Interactiva:** Visualización analítica de las fluctuaciones de precios mediante gráficos temporales dinámicos.
*   **Persistencia Local Eficiente:** Arquitectura embebida para el almacenamiento seguro y rápido de las consultas y productos monitorizados.
*   **Sistema de Notificaciones Integrado:** Envío automático de alertas instantáneas a dispositivos móviles cuando se detectan bajadas de precio o cambios de disponibilidad.

---

## 🏗️ Arquitectura y Componentes Técnicos

El sistema se divide en tres capas fundamentales estructuradas bajo principios de modularidad y código limpio:

### 1. Interfaz de Usuario (`app.py`)
Desarrollada con **Streamlit**, proporciona un cuadro de mando ágil e intuitivo desde el navegador web sin la sobrecarga de los entornos de escritorio tradicionales. Permite la gestión de productos, configuración de umbrales de alerta y visualización analítica de datos mediante **Plotly**.

### 2. Motor de Extracción y Lógica de Negocio (`logic.py`)
*   **Análisis HTML:** Implementado con **Beautiful Soup 4** para el aislamiento de scripts específicos dentro del código fuente de los portales comerciales.
*   **Extracción por Estándares (JSON-LD):** En lugar de depender de selectores CSS o XPath propensos a romperse con rediseños visuales, el script localiza y parsea bloques de datos estructurados basados en el estándar global de **Schema.org** y las directrices de **Google Search Central**. Esto garantiza la consistencia de los datos de producto, precio, divisa y *stock*.
*   **Mimetismo Perimetral:** Incorporación de cabeceras HTTP dinámicas (`User-Agent`) y gestión de sesiones para mitigar bloqueos perimetrales automáticos.

### 3. Persistencia de Datos
Uso del motor relacional embebido **SQLite3**. Toda la información se centraliza de manera transaccional en un único archivo de disco local, optimizando los tiempos de respuesta y garantizando la total portabilidad del sistema sin necesidad de desplegar infraestructura externa de servidores.

### 4. Canal de Alertas
Integración directa con la **Telegram Bot API**. El sistema utiliza credenciales seguras gestionadas a través de interacciones previas con **BotFather** para automatizar el envío asíncrono de alertas push directamente al canal del usuario.

---

## 🛠️ Tecnologías y Librerías Utilizadas

*   **Lenguaje:** Python 3.10+
*   **Extracción de Datos:** Beautiful Soup 4, Requests
*   **Interfaz Gráfica:** Streamlit, Plotly Express
*   **Base de Datos:** SQLite3 (Interfaz nativa DB-API 2.0)
*   **Notificaciones:** Telegram Bot API (HTTP POST requests)

---

## 🚀 Instalación y Despliegue Local

Sigue estos pasos para clonar el repositorio e iniciar la aplicación en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone https://github.com/Sg2lk/Scrapper.git
cd Scrapper
```

### 2. Crear y activar un entorno virtual (Recomendado)
```
# En Windows:
python -m venv venv
.\venv\Scripts\activate

# En macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias necesarias
```
pip install -r requirements.txt
```

### 3.5. Configuración de Credenciales y Variables de Entorno 🔑

Para que el sistema de alertas de Telegram funcione correctamente, es necesario configurar las credenciales de la API de forma segura. El proyecto está diseñado para leer estas variables de entorno sin exponer los tokens en el código fuente público.

1. En la carpeta raíz del proyecto, crea un archivo llamado `.env` (o si utilizas la configuración nativa de Streamlit, crea el archivo `.streamlit/secrets.toml`).
2. Abre el archivo con cualquier editor de texto y añade tus credenciales oficiales de Telegram siguiendo este formato:

```ini
# Configuración de Telegram API
TELEGRAM_TOKEN="TU_TOKEN_DE_BOT_AQUÍ"
TELEGRAM_CHAT_ID="TU_ID_DE_CHAT_DE_TELEGRAM_AQUÍ"
```

💡 ¿Cómo obtener estas credenciales?

- TELEGRAM_TOKEN: Consíguelo iniciando una conversación en Telegram con el bot oficial @BotFather. Utiliza el comando /newbot, asígnale un nombre a tu bot y copia el token HTTP API que te generará al instante

- TELEGRAM_CHAT_ID: Es el identificador numérico de tu chat privado con tu bot para recibir las alertas. Puedes obtenerlo enviando cualquier mensaje a tu nuevo bot y consultando su historial de actualizaciones, o utilizando bots públicos de utilidad como @userinfobot.

Nota: El archivo .env (o la carpeta .streamlit) está incluido en el archivo .gitignore para garantizar que tus claves privadas nunca se suban a GitHub por error.

### 4. Ejecutar la aplicación web

Dispones de dos métodos para iniciar el panel de control:

#### Método A: Ejecución Manual (Consola)
Si prefieres lanzar el servidor desde la terminal, ejecuta el siguiente comando con el entorno virtual activo:
```
streamlit run app.py
```

#### Método B: Ejecución Automatizada en Windows (Automatización en un clic) ⚡

Para facilitar el despliegue diario y la experiencia de usuario sin necesidad de interactuar con la línea de comandos, el proyecto incluye un script ejecutable automatizado para entornos Windows: run.bat

Este script automatiza de forma secuencial las siguientes tareas del sistema:

**1.** Abre la consola de comandos de Windows en segundo plano.

**2.** Activa automáticamente el entorno virtual privado de Python (venv).

**3.** Lanza el servidor local de Streamlit apuntando a la arquitectura de app.py.

**4.** Abre de forma directa tu navegador web predeterminado en la interfaz del proyecto.

**Instrucciones de uso**: Simplemente dirígete a la carpeta raíz del proyecto y haz doble clic sobre el archivo ejecutable. El monitor de precios se iniciará solo en un segundo.
