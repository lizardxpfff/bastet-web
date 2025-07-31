import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import requests
import sqlite3
import folium
import webbrowser
from tkinterweb import HtmlFrame
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
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitud},{longitud}&key=AIzaSyCrcD5dnO3F61BT6HLbPgGJ-hrQASOiXKg"
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
        popup = folium.Popup(f"<b>Propietario:</b> {camara[3]}<br><b>Coordenadas:</b> {camara[1]}, {camara[2]}<br><b>Contacto:</b> {camara[4]}", max_width=300)
        folium.Marker(
            [camara[1], camara[2]],
            tooltip=f"Propietario: {camara[3]}",
            popup=popup,
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
    conn.close()
    if camaras_cercanas:
        mostrar_mapa(latitud, longitud, camaras_cercanas)
    else:
        # Mostrar el mapa vacío igual en el navegador
        mapa = folium.Map(location=[latitud, longitud], zoom_start=16)
        folium.Marker([latitud, longitud], tooltip="Ubicación buscada", icon=folium.Icon(color='blue')).add_to(mapa)
        mapa_path = os.path.abspath("camaras_mapa.html")
        mapa.save(mapa_path)
        webbrowser.open(f"file://{mapa_path}")

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


# --- Crear la ventana principal ---
root = tk.Tk()
root.title("Consulta de Cámaras")
root.geometry("520x420")
root.configure(bg="#eaf0fa")

# --- Estilos modernos con ttk ---
style = ttk.Style()
style.theme_use('clam')
style.configure('TFrame', background="#eaf0fa")
style.configure('TLabel', background="#eaf0fa", foreground="#1E3A5F", font=("Segoe UI", 12))
style.configure('TButton', font=("Segoe UI", 11, "bold"), padding=6, background="#4A90E2", foreground="white")
style.map('TButton', background=[('active', '#1C3D6D')])

# --- Frame principal ---
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")

# --- Título ---
title_label = ttk.Label(main_frame, text="Consulta de Cámaras", font=("Segoe UI", 18, "bold"), anchor="center")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

# --- Entradas de latitud y longitud ---
label_latitud = ttk.Label(main_frame, text="Latitud:")
label_latitud.grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_latitud = ttk.Entry(main_frame, font=("Segoe UI", 12), width=22)
entry_latitud.grid(row=1, column=1, padx=10, pady=10, sticky="w")

label_longitud = ttk.Label(main_frame, text="Longitud:")
label_longitud.grid(row=2, column=0, padx=10, pady=10, sticky="e")
entry_longitud = ttk.Entry(main_frame, font=("Segoe UI", 12), width=22)
entry_longitud.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# --- Botones principales ---
boton_buscar = ttk.Button(main_frame, text="Buscar Cámaras", command=buscar_camaras)
boton_buscar.grid(row=3, column=0, padx=10, pady=15, sticky="ew")

boton_limpiar = ttk.Button(main_frame, text="Limpiar", command=limpiar_campos)
boton_limpiar.grid(row=3, column=1, padx=10, pady=15, sticky="ew")

boton_agregar_camara = ttk.Button(main_frame, text="Agregar Cámara", command=abrir_submenu_agregar_camara)
boton_agregar_camara.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

boton_salir = ttk.Button(main_frame, text="Salir", command=root.quit)
boton_salir.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

# --- Mejorar el submenú de agregar cámara ---
def abrir_submenu_agregar_camara():
    ventana_agregar_camara = tk.Toplevel(root)
    ventana_agregar_camara.title("Agregar Cámara")
    ventana_agregar_camara.configure(bg="#eaf0fa")
    frame = ttk.Frame(ventana_agregar_camara, padding=20)
    frame.pack(expand=True, fill="both")

    label_latitud_camara = ttk.Label(frame, text="Latitud:")
    label_latitud_camara.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_latitud_camara = ttk.Entry(frame, font=("Segoe UI", 12), width=22)
    entry_latitud_camara.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    label_longitud_camara = ttk.Label(frame, text="Longitud:")
    label_longitud_camara.grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_longitud_camara = ttk.Entry(frame, font=("Segoe UI", 12), width=22)
    entry_longitud_camara.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    label_propietario_camara = ttk.Label(frame, text="Propietario:")
    label_propietario_camara.grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_propietario_camara = ttk.Entry(frame, font=("Segoe UI", 12), width=22)
    entry_propietario_camara.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    label_contacto_camara = ttk.Label(frame, text="Contacto:")
    label_contacto_camara.grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_contacto_camara = ttk.Entry(frame, font=("Segoe UI", 12), width=22)
    entry_contacto_camara.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    boton_guardar_camara = ttk.Button(
        frame, text="Guardar Datos",
        command=lambda: almacenar_camara(entry_latitud_camara, entry_longitud_camara, entry_propietario_camara, entry_contacto_camara)
    )
    boton_guardar_camara.grid(row=4, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

root.mainloop()