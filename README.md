# Bastet — Aplicación web para consulta de cámaras

Esta es la versión web del proyecto Bastet. Es una pequeña aplicación web hecha con Flask que permite:

- Buscar cámaras cercanas a unas coordenadas (latitud/longitud).
- Agregar cámaras (con propietario, contacto y una imagen opcional).
- Ver las cámaras resultantes sobre un mapa generado con Folium.

Datos técnicos y comportamiento:

- La aplicación usa una base de datos SQLite local (`camaras.db`). Si no existe, se crea automáticamente al iniciar la app.
- Las imágenes subidas se guardan en `static/imagenes/` y se sirven desde la carpeta `static`.
- La aplicación incluye un login simulado (acepta cualquier usuario/clave) y protege las rutas principales.

## Requisitos

- Python 3.8+ (probado en 3.11)
- pip

## Instalación (local / desarrollo)

Recomendado: usar un entorno virtual.

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
# Desde la raíz del proyecto
export FLASK_APP=app.py
export FLASK_ENV=development   # opcional: activa auto-reload y debug
flask run

# o directamente
python app.py
```

La aplicación quedará disponible en http://127.0.0.1:5000.



## Dependencias

- Flask
- folium

Se incluyen en `requirements.txt`.

## Siguientes pasos recomendados

- Añadir un `requirements.txt` (ya incluido en este repo).
- Añadir un archivo `.env` para variables sensibles (SECRET_KEY) y usar `python-dotenv`/config desde Flask.
- Crear tests básicos y/o configurar GitHub Actions para CI.
