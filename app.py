from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import folium

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambiar

DATABASE = 'camaras.db'
UPLOAD_FOLDER = os.path.join('static', 'imagenes')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- Función para conectar a la base de datos ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Función para inicializar la base de datos (igual que en Tkinter) ---
def inicializar_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camaras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitud REAL,
            longitud REAL,
            propietario TEXT,
            contacto TEXT,
            imagen TEXT
        )
    ''')
    conn.commit()
    conn.close()

inicializar_db()

# --- Login simulado tipo Active Directory ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        clave = request.form.get('clave')
        # Simulación: acepta cualquier usuario/clave
        if usuario and clave:
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            flash('Ingrese usuario y contraseña.', 'danger')
    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Decorador para requerir login ---
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Página principal: búsqueda de cámaras ---
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    camaras = []
    latitud = longitud = None
    if request.method == 'POST':
        if 'limpiar' in request.form:
            # Botón limpiar: borra campos y resultados
            return render_template('index.html', camaras=[], latitud='', longitud='')
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        try:
            latitud = float(latitud)
            longitud = float(longitud)
            radio = 0.0018
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM camaras WHERE latitud BETWEEN ? AND ? AND longitud BETWEEN ? AND ?",
                           (latitud-radio, latitud+radio, longitud-radio, longitud+radio))
            camaras = cursor.fetchall()
            conn.close()
        except Exception:
            flash('Latitud y longitud deben ser números válidos. Ej: -33.602145315186874, -70.57746968055821', 'danger')
    return render_template('index.html', camaras=camaras, latitud=latitud, longitud=longitud)

# --- Página para agregar una cámara ---
@app.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar_camara():
    if request.method == 'POST':
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        propietario = request.form.get('propietario')
        contacto = request.form.get('contacto')
        imagen = request.files.get('imagen')
        imagen_url = request.form.get('imagen_url')
        imagen_path = ''
        if imagen and imagen.filename != '':
            ext = imagen.filename.rsplit('.', 1)[-1].lower()
            if ext in ALLOWED_EXTENSIONS:
                filename = imagen.filename
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                imagen.save(save_path)
                imagen_path = url_for('static', filename=f'imagenes/{filename}')
            else:
                flash('Formato de imagen no permitido.', 'danger')
                return redirect(request.url)
        elif imagen_url:
            imagen_path = imagen_url
        if not (latitud and longitud and propietario and contacto):
            flash('Por favor, complete todos los campos obligatorios.', 'danger')
            return redirect(request.url)
        try:
            latitud = float(latitud)
            longitud = float(longitud)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO camaras (latitud, longitud, propietario, contacto, imagen) VALUES (?, ?, ?, ?, ?)",
                           (latitud, longitud, propietario, contacto, imagen_path))
            conn.commit()
            conn.close()
            flash('Cámara agregada con éxito.', 'success')
            return redirect(url_for('index'))
        except Exception:
            flash('Error al guardar la cámara.', 'danger')
    return render_template('agregar_camara.html')

# --- Página para ver el mapa con las cámaras encontradas ---
@app.route('/mapa')
@login_required
def mapa():
    latitud = request.args.get('latitud', type=float)
    longitud = request.args.get('longitud', type=float)
    camaras = []
    if latitud is not None and longitud is not None:
        radio = 0.0018
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM camaras WHERE latitud BETWEEN ? AND ? AND longitud BETWEEN ? AND ?",
                       (latitud-radio, latitud+radio, longitud-radio, longitud+radio))
        camaras = cursor.fetchall()
        conn.close()
    # Generar mapa con Folium
    mapa = folium.Map(location=[latitud or 0, longitud or 0], zoom_start=16)
    if latitud and longitud:
        folium.Marker([latitud, longitud], tooltip="Ubicación buscada", icon=folium.Icon(color='blue')).add_to(mapa)
    for cam in camaras:
        popup = folium.Popup(f"<b>Propietario:</b> {cam['propietario']}<br><b>Coordenadas:</b> {cam['latitud']}, {cam['longitud']}<br><b>Contacto:</b> {cam['contacto']}", max_width=300)
        folium.Marker(
            [cam['latitud'], cam['longitud']],
            tooltip=f"Propietario: {cam['propietario']}",
            popup=popup,
            icon=folium.Icon(color='red', icon='camera')
        ).add_to(mapa)
    mapa_path = os.path.join('static', 'camaras_mapa.html')
    mapa.save(mapa_path)
    return render_template('mapa.html', mapa_file=mapa_path)

if __name__ == '__main__':
    app.run(debug=True)
