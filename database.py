import sqlite3

def conectar_db():
    return sqlite3.connect('precios.db')

def inicializar_db():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            tienda TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            precio REAL NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    ''')

    conexion.commit()
    conexion.close()
    print("✅ Base de datos inicializada correctamente.")

if __name__ == "__main__":
    inicializar_db()