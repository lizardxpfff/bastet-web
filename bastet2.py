import tkinter as tk
import tkinter.messagebox as messagebox
import requests
import sqlite3
import folium
import webbrowser
import os

# --- Inicializar base de datos ---
def inicializar_db():
    conn = sqlite3.connect('camaras.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camaras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitud REAL,
            longitud REAL,
            propietario TEXT,
            contacto TEXT
        )
    ''')
    conn.commit()
    conn.close()

inicializar_db()

# --- Función para obtener la dirección desde la API de Google Maps ---
def obtener_direccion(latitud, longitud):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitud},{longitud}&key=null"
        response = requests.get(url)
        data = response.json()
        if data['status'] == 'OK' and data['results']:
            return data['results'][0]['formatted_address']
        else:
            return "Dirección no encontrada"
    except Exception as e:
        return f"Error: {e}"

# --- Función para mostrar el mapa con las cámaras ---
def mostrar_mapa(latitud, longitud, camaras):
    mapa = folium.Map(location=[latitud, longitud], zoom_start=16)
    folium.Marker([latitud, longitud], tooltip="Ubicación buscada", icon=folium.Icon(color='blue')).add_to(mapa)
    for camara in camaras:
        folium.Marker(
            [camara[1], camara[2]],
            tooltip=f"Propietario: {camara[3]}\nContacto: {camara[4]}",
            icon=folium.Icon(color='red', icon='camera')
        ).add_to(mapa)
    mapa_path = os.path.abspath("camaras_mapa.html")
    mapa.save(mapa_path)
    webbrowser.open(f"file://{mapa_path}")

# --- Función para almacenar la ubicación de una cámara en la base de datos ---
def almacenar_camara(entry_latitud_camara, entry_longitud_camara, entry_propietario_camara, entry_contacto_camara):
    latitud = entry_latitud_camara.get()
    longitud = entry_longitud_camara.get()
    propietario = entry_propietario_camara.get()
    contacto = entry_contacto_camara.get()
    
    if not latitud or not longitud or not propietario or not contacto:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    try:
        latitud = float(latitud)
        longitud = float(longitud)
        if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Latitud y longitud deben ser números válidos.")
        return
    
    conn = sqlite3.connect('camaras.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO camaras (latitud, longitud, propietario, contacto) VALUES (?, ?, ?, ?)",
                   (latitud, longitud, propietario, contacto))
    conn.commit()
    conn.close()
    
    entry_latitud_camara.delete(0, tk.END)
    entry_longitud_camara.delete(0, tk.END)
    entry_propietario_camara.delete(0, tk.END)
    entry_contacto_camara.delete(0, tk.END)
    
    messagebox.showinfo("Éxito", "Los datos han sido guardados con éxito.")

# --- Función para buscar cámaras cercanas y mostrar mapa ---
def buscar_camaras():
    latitud = entry_latitud.get()
    longitud = entry_longitud.get()
    try:
        latitud = float(latitud)
        longitud = float(longitud)
        if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Latitud y longitud deben ser números válidos.")
        return

    direccion = obtener_direccion(latitud, longitud)
    conn = sqlite3.connect('camaras.db')
    cursor = conn.cursor()
    radio = 0.0018
    cursor.execute("SELECT * FROM camaras WHERE latitud BETWEEN ? AND ? AND longitud BETWEEN ? AND ?",
                   (latitud-radio, latitud+radio, longitud-radio, longitud+radio))
    camaras_cercanas = cursor.fetchall()
    mensaje = f"Dirección: {direccion}\n\nCámaras cercanas:\n"
    for camara in camaras_cercanas:
        mensaje += f"\nPropietario: {camara[3]}\nCoordenadas: {camara[1]}, {camara[2]}\nContacto: {camara[4]}\n\n"
    messagebox.showinfo("Resultado de la búsqueda", mensaje)
    conn.close()
    if camaras_cercanas:
        mostrar_mapa(latitud, longitud, camaras_cercanas)
    else:
        messagebox.showinfo("Mapa", "No se encontraron cámaras cercanas para mostrar en el mapa.")

# --- Función para limpiar los campos de entrada ---
def limpiar_campos():
    entry_latitud.delete(0, tk.END)
    entry_longitud.delete(0, tk.END)

# --- Función para abrir el submenú de agregar cámara ---
def abrir_submenu_agregar_camara():
    ventana_agregar_camara = tk.Toplevel(root)
    ventana_agregar_camara.title("Agregar Cámara")
    
    label_latitud_camara = tk.Label(ventana_agregar_camara, text="Latitud:")
    label_latitud_camara.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    entry_latitud_camara = tk.Entry(ventana_agregar_camara)
    entry_latitud_camara.grid(row=0, column=1, padx=10, pady=10)

    label_longitud_camara = tk.Label(ventana_agregar_camara, text="Longitud:")
    label_longitud_camara.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    entry_longitud_camara = tk.Entry(ventana_agregar_camara)
    entry_longitud_camara.grid(row=1, column=1, padx=10, pady=10)

    label_propietario_camara = tk.Label(ventana_agregar_camara, text="Propietario:")
    label_propietario_camara.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    entry_propietario_camara = tk.Entry(ventana_agregar_camara)
    entry_propietario_camara.grid(row=2, column=1, padx=10, pady=10)

    label_contacto_camara = tk.Label(ventana_agregar_camara, text="Contacto:")
    label_contacto_camara.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    entry_contacto_camara = tk.Entry(ventana_agregar_camara)
    entry_contacto_camara.grid(row=3, column=1, padx=10, pady=10)

    boton_guardar_camara = tk.Button(
        ventana_agregar_camara, text="Guardar Datos",
        command=lambda: almacenar_camara(entry_latitud_camara, entry_longitud_camara, entry_propietario_camara, entry_contacto_camara)
    )
    boton_guardar_camara.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Crear la ventana principal
root = tk.Tk()
root.title("Consulta de Cámaras")
root.geometry("500x400")
root.configure(bg="#1E3A5F")
btn_color = "#4A90E2"
btn_hover_color = "#1C3D6D"

def on_enter(e):
    e.widget['background'] = btn_hover_color

def on_leave(e):
    e.widget['background'] = btn_color

boton_buscar = tk.Button(root, text="Buscar Cámaras", command=buscar_camaras, bg=btn_color, fg="white", font=("Arial", 12))
boton_buscar.grid(row=0, column=1, padx=10, pady=10)
boton_buscar.bind("<Enter>", on_enter)
boton_buscar.bind("<Leave>", on_leave)

boton_limpiar = tk.Button(root, text="Limpiar", command=limpiar_campos, bg=btn_color, fg="white", font=("Arial", 12))
boton_limpiar.grid(row=1, column=0, padx=10, pady=10)
boton_limpiar.bind("<Enter>", on_enter)
boton_limpiar.bind("<Leave>", on_leave)

boton_salir = tk.Button(root, text="Salir", command=root.quit, bg=btn_color, fg="white", font=("Arial", 12))
boton_salir.grid(row=1, column=1, padx=10, pady=10)
boton_salir.bind("<Enter>", on_enter)
boton_salir.bind("<Leave>", on_leave)

boton_agregar_camara = tk.Button(root, text="Agregar Cámara", command=abrir_submenu_agregar_camara, bg=btn_color, fg="white", font=("Arial", 12))
boton_agregar_camara.grid(row=0, column=0, padx=10, pady=10)
boton_agregar_camara.bind("<Enter>", on_enter)
boton_agregar_camara.bind("<Leave>", on_leave)

label_latitud = tk.Label(root, text="Latitud:", bg="#1E3A5F", fg="white", font=("Arial", 12))
label_latitud.grid(row=2, column=0, padx=10, pady=10, sticky="w")

entry_latitud = tk.Entry(root, font=("Arial", 12))
entry_latitud.grid(row=2, column=1, padx=10, pady=10)

label_longitud = tk.Label(root, text="Longitud:", bg="#1E3A5F", fg="white", font=("Arial", 12))
label_longitud.grid(row=3, column=0, padx=10, pady=10, sticky="w")

entry_longitud = tk.Entry(root, font=("Arial", 12))
entry_longitud.grid(row=3, column=1, padx=10, pady=10)

root.mainloop()